import time
import threading
import logging
from typing import Optional, Dict, Any, Callable
from src.app.queue.adapter import QueueAdapter
from src.app.streaming.broker import Broker
from src.app.repos.request_repo import RequestRepo
from src.app.streaming.worker import StreamingWorker
from src.app.streaming.cancellation import CancellationCoordinator
from src.app.config import Settings

logger = logging.getLogger(__name__)

class WorkerRunner:
    """
    Polls the queue, reserves jobs, and executes them via StreamingWorker.
    """
    def __init__(
        self,
        queue_adapter: QueueAdapter,
        broker: Broker,
        request_repo: RequestRepo,
        streaming_worker_factory: Callable[[], StreamingWorker],
        cancellation_coordinator: CancellationCoordinator,
        settings: Settings = Settings()
    ):
        self.queue = queue_adapter
        self.broker = broker
        self.repo = request_repo
        self.worker_factory = streaming_worker_factory
        self.cancel_coord = cancellation_coordinator
        self.settings = settings

    def run_once(self, queue_name: str = "default") -> Optional[Dict[str, Any]]:
        """
        Processes a single job from the queue.
        """
        # 1. Reserve Job
        job = self.queue.reserve(queue_name)
        if not job:
            return None

        job_id = job["id"]
        # Payload structure depends on what we enqueued. 
        # Assuming payload is inside 'payload' key or is the job itself.
        payload = job.get("payload", job)
        
        request_id = payload.get("request_id")
        if not request_id:
            logger.error(f"Job {job_id} missing request_id. Acknowledging to remove.")
            self.queue.ack(queue_name, job_id)
            return None

        logger.info(f"Processing job {job_id} for request {request_id}")

        try:
            # 2. Update Status
            self.repo.update_request_status(request_id, "running")

            # 3. Create Worker & Token
            worker = self.worker_factory()
            token = self.cancel_coord.get_or_create_token(request_id)

            # 4. Execute
            # We need to capture the output. The worker publishes to the broker.
            # But for the runner, we might want to know if it succeeded.
            # The worker.handle_request is a generator or async? 
            # In our previous step, StreamingWorker.process_request was async/generator.
            # But here we are in a synchronous runner (per requirements).
            # We'll assume we can run it synchronously or wrap it.
            # If StreamingWorker is async, we need async runner. 
            # Requirement says "Keep code synchronous (no async) for simplicity".
            # But StreamingWorker was designed for FastAPI (async).
            # We will assume for this step that we can call it synchronously or it has a sync wrapper.
            # Actually, looking at previous steps, StreamingWorker uses `async def`.
            # To run async code in sync runner, we need `asyncio.run`.
            
            import asyncio
            
            async def _execute():
                # We iterate the generator to ensure it runs to completion
                async for _ in worker.process_request(
                    request_id=request_id,
                    prompt=payload.get("prompt", ""),
                    model=payload.get("model", self.settings.DEFAULT_MODEL),
                    stream=payload.get("stream", True)
                ):
                    pass # Just consume the stream

            asyncio.run(_execute())

            # 5. Success
            self.repo.update_request_status(request_id, "done")
            self.repo.record_usage(request_id, 0, 0, 0.0) # Placeholders
            self.queue.ack(queue_name, job_id)
            
            return {"request_id": request_id, "status": "success", "attempts": job.get("attempts", 1)}

        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}")
            
            attempts = job.get("attempts", 1)
            if attempts < self.settings.QUEUE_MAX_ATTEMPTS:
                # Retry with backoff
                delay = 2 ** attempts # 2, 4, 8 seconds...
                logger.info(f"Retrying job {job_id} in {delay}s (Attempt {attempts})")
                self.queue.requeue(queue_name, job, delay_seconds=delay)
                self.repo.update_request_status(request_id, "pending", error_message=str(e))
                return {"request_id": request_id, "status": "retried", "attempts": attempts}
            else:
                # Fail / DLQ
                logger.error(f"Job {job_id} exceeded max attempts. Moving to DLQ.")
                self.queue.fail(queue_name, job_id, reason=str(e))
                self.repo.update_request_status(request_id, "failed", error_message=str(e))
                return {"request_id": request_id, "status": "failed", "attempts": attempts}

    def run_forever(self, queue_name: str = "default", stop_event: Optional[threading.Event] = None):
        logger.info(f"Worker runner started for queue: {queue_name}")
        while not (stop_event and stop_event.is_set()):
            result = self.run_once(queue_name)
            if not result:
                # Empty queue, sleep briefly
                time.sleep(1)
