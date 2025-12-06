from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class QueueAdapter(ABC):
    """
    Abstract base class for queue adapters.
    """
    
    @abstractmethod
    def enqueue(self, queue_name: str, job: Dict[str, Any]) -> str:
        """
        Enqueues a job.
        Returns the job ID.
        """
        pass

    @abstractmethod
    def reserve(self, queue_name: str, timeout: Optional[int] = 0) -> Optional[Dict[str, Any]]:
        """
        Atomically reserves a job from the queue.
        The job should be hidden from other workers for a visibility timeout.
        Returns the job dict or None if queue is empty.
        """
        pass

    @abstractmethod
    def ack(self, queue_name: str, job_id: str) -> None:
        """
        Acknowledges successful processing of a job, removing it from the queue.
        """
        pass

    @abstractmethod
    def fail(self, queue_name: str, job_id: str, reason: Optional[str] = None) -> None:
        """
        Marks a job as failed. Depending on implementation, might move to DLQ.
        """
        pass

    @abstractmethod
    def requeue(self, queue_name: str, job: Dict[str, Any], delay_seconds: Optional[int] = 0) -> str:
        """
        Re-enqueues a job, potentially with a delay (backoff).
        """
        pass

    @abstractmethod
    def inspect_queue_length(self, queue_name: str) -> int:
        """
        Returns the approximate number of messages in the queue.
        """
        pass
