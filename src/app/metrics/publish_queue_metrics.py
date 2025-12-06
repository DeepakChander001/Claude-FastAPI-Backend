import logging
from typing import Optional, Any, Protocol
from src.app.queue.adapter import QueueAdapter

logger = logging.getLogger(__name__)

class MetricsPusher(Protocol):
    def put_metric(self, name: str, value: float, unit: str = "Count") -> None:
        ...

class FakeMetricsPusher:
    """
    In-memory metrics recorder for testing.
    """
    def __init__(self):
        self.metrics = {}

    def put_metric(self, name: str, value: float, unit: str = "Count") -> None:
        logger.info(f"[FakeMetric] {name}: {value} {unit}")
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

class CloudWatchPusher:
    """
    Publishes metrics to CloudWatch.
    Guarded import to prevent boto3 requirement in local/test envs.
    """
    def __init__(self, namespace: str = "ClaudeProxy/Queue"):
        self.namespace = namespace
        self.client = None
        try:
            import boto3
            self.client = boto3.client("cloudwatch")
        except ImportError:
            logger.warning("boto3 not installed, CloudWatchPusher disabled")

    def put_metric(self, name: str, value: float, unit: str = "Count") -> None:
        if not self.client:
            return
        
        try:
            self.client.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        "MetricName": name,
                        "Value": value,
                        "Unit": unit
                    }
                ]
            )
        except Exception as e:
            logger.error(f"Failed to push metric {name}: {e}")

def publish_queue_metrics(queue_adapter: QueueAdapter, pusher: Optional[MetricsPusher] = None) -> None:
    """
    Collects queue metrics and pushes them.
    """
    if pusher is None:
        pusher = FakeMetricsPusher()

    try:
        # 1. Queue Depth
        depth = queue_adapter.inspect_queue_length("default")
        pusher.put_metric("QueueDepth", float(depth), "Count")

        # 2. Oldest Message Age (Not supported by all adapters directly, 
        # but we can simulate or add to interface later. For now, we skip or mock).
        # If adapter supported it: age = queue_adapter.get_oldest_age("default")
        # pusher.put_metric("OldestMessageAge", age, "Seconds")
        
    except Exception as e:
        logger.error(f"Error publishing queue metrics: {e}")
