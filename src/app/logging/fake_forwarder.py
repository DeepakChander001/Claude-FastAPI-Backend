from typing import List, Dict, Any

class FakeLogForwarder:
    """
    Captures logs in memory for testing verification.
    """
    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def emit(self, record: Dict[str, Any]):
        self.records.append(record)

    def get_records_by_request_id(self, request_id: str) -> List[Dict[str, Any]]:
        return [r for r in self.records if r.get("request_id") == request_id]

    def clear(self):
        self.records = []

class FakeTraceCollector:
    """
    Captures spans in memory.
    """
    def __init__(self):
        self.spans = []

    def add_span(self, span):
        self.spans.append(span)
