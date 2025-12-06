import pytest
from unittest.mock import MagicMock, patch
from src.app.queue.fake_queue import FakeQueue
from src.app.metrics.publish_queue_metrics import publish_queue_metrics, FakeMetricsPusher

def test_publish_queue_metrics():
    # Setup
    queue = FakeQueue()
    queue.enqueue("default", {"id": "1"})
    queue.enqueue("default", {"id": "2"})
    
    pusher = FakeMetricsPusher()
    
    # Execute
    publish_queue_metrics(queue, pusher)
    
    # Verify
    assert "QueueDepth" in pusher.metrics
    assert pusher.metrics["QueueDepth"][-1] == 2.0

def test_canary_script_logic_simulation():
    """
    Simulates the logic of a canary release script decision.
    """
    # Inputs
    canary_percent = 10
    alarms_triggered = False
    smoke_test_passed = True
    
    # Logic
    should_promote = not alarms_triggered and smoke_test_passed
    should_rollback = alarms_triggered or not smoke_test_passed
    
    assert should_promote is True
    assert should_rollback is False
    
    # Simulate failure
    alarms_triggered = True
    should_promote = not alarms_triggered and smoke_test_passed
    should_rollback = alarms_triggered or not smoke_test_passed
    
    assert should_promote is False
    assert should_rollback is True
