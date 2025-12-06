import pytest
import time
from unittest.mock import MagicMock
from src.app.queue.fake_queue import FakeQueue
from src.app.worker.runner import WorkerRunner
from src.app.repos.fake_request_repo import FakeRequestRepo
from src.app.streaming.fakes import FakeBroker, FakeCancellationCoordinator, FakeStreamingWorker
from src.app.config import Settings

def test_fake_queue_operations():
    queue = FakeQueue()
    
    # 1. Enqueue
    job_id = queue.enqueue("test-queue", {"foo": "bar"})
    assert job_id
    assert queue.inspect_queue_length("test-queue") == 1
    
    # 2. Reserve
    job = queue.reserve("test-queue")
    assert job
    assert job["id"] == job_id
    assert job["payload"]["foo"] == "bar"
    assert queue.inspect_queue_length("test-queue") == 0 # Reserved is not visible
    
    # 3. Ack
    queue.ack("test-queue", job_id)
    assert len(queue.reserved) == 0

def test_fake_queue_dlq():
    queue = FakeQueue()
    job_id = queue.enqueue("test-queue", {"data": 1})
    
    # Reserve and Fail
    queue.reserve("test-queue")
    queue.fail("test-queue", job_id, reason="failed")
    
    assert len(queue.dlq) == 1
    assert queue.dlq[0].id == job_id

def test_worker_runner_success():
    # Setup
    queue = FakeQueue()
    broker = FakeBroker()
    repo = FakeRequestRepo()
    cancel_coord = FakeCancellationCoordinator()
    
    # Enqueue a job
    request_id = "req-123"
    repo.create_request(request_id, prompt="hello")
    queue.enqueue("default", {"request_id": request_id, "prompt": "hello"})
    
    # Factory for worker
    def worker_factory():
        return FakeStreamingWorker(broker, cancel_coord)
        
    runner = WorkerRunner(queue, broker, repo, worker_factory, cancel_coord)
    
    # Run
    result = runner.run_once("default")
    
    # Verify
    assert result["status"] == "success"
    assert repo.get_request_status(request_id)["status"] == "done"
    assert queue.inspect_queue_length("default") == 0

def test_worker_runner_retry_flow():
    # Setup
    queue = FakeQueue()
    broker = FakeBroker()
    repo = FakeRequestRepo()
    cancel_coord = FakeCancellationCoordinator()
    settings = Settings(QUEUE_MAX_ATTEMPTS=2)
    
    request_id = "req-retry"
    repo.create_request(request_id, prompt="fail me")
    queue.enqueue("default", {"request_id": request_id, "prompt": "fail me"})
    
    # Mock worker to fail
    mock_worker = MagicMock()
    # Async generator mock is tricky, so we use a real class that fails?
    # Or we just mock the factory to return something that raises.
    # But runner calls `process_request` which returns an async generator.
    
    class FailingWorker:
        async def process_request(self, *args, **kwargs):
            raise ValueError("Boom")
            yield # make it a generator
            
    runner = WorkerRunner(queue, broker, repo, lambda: FailingWorker(), cancel_coord, settings)
    
    # Run 1: Should Retry
    result = runner.run_once("default")
    assert result["status"] == "retried"
    assert result["attempts"] == 1
    assert repo.get_request_status(request_id)["status"] == "pending"
    
    # Queue should have it back (delayed)
    # FakeQueue puts it back immediately if we don't check time, 
    # but visible_after is set. FakeQueue.reserve checks visibility.
    # We need to advance time or just check internal state.
    assert len(queue.queues["default"]) == 1
    job = queue.queues["default"][0]
    assert job.attempts == 1
    assert job.visible_after is not None
    
    # Force visibility for next run
    job.visible_after = None 
    
    # Run 2: Should Fail (Max attempts 2 reached? No, attempts=1 < 2. Next run makes attempts=2)
    # Wait, logic is: if attempts < max_attempts. 
    # Current attempts is 1. Max is 2. 1 < 2 is True. So it retried.
    # Next run: reserve increments attempts to 2.
    # Exception happens. attempts=2. 2 < 2 is False. So Fail.
    
    result = runner.run_once("default")
    assert result["status"] == "failed"
    assert repo.get_request_status(request_id)["status"] == "failed"
    assert len(queue.dlq) == 1
