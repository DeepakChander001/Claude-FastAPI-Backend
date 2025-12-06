from typing import Dict, List, Any

class FakeMetric:
    def __init__(self):
        self.values: Dict[str, Any] = {}

    def labels(self, **kwargs):
        key = tuple(sorted(kwargs.items()))
        if key not in self.values:
            self.values[key] = 0
        return self

    def inc(self, amount=1):
        # This is a bit tricky because labels() returns self, 
        # but we need to know WHICH key to increment.
        # Simplified: We'll assume the last call to labels() set a 'current_key'
        # This is not thread-safe but fine for simple sync tests.
        pass

class FakeCounter:
    def __init__(self):
        self.data = {} # (labels_tuple) -> count

    def labels(self, **kwargs):
        self._current_labels = tuple(sorted(kwargs.items()))
        if self._current_labels not in self.data:
            self.data[self._current_labels] = 0
        return self

    def inc(self, amount=1):
        self.data[self._current_labels] += amount

class FakeHistogram:
    def __init__(self):
        self.data = {} # (labels_tuple) -> list of observations

    def labels(self, **kwargs):
        self._current_labels = tuple(sorted(kwargs.items()))
        if self._current_labels not in self.data:
            self.data[self._current_labels] = []
        return self

    def observe(self, value):
        self.data[self._current_labels].append(value)

class FakeGauge:
    def __init__(self):
        self.data = {} # (labels_tuple) -> value

    def labels(self, **kwargs):
        self._current_labels = tuple(sorted(kwargs.items()))
        if self._current_labels not in self.data:
            self.data[self._current_labels] = 0
        return self

    def inc(self, amount=1):
        self.data[self._current_labels] += amount

    def dec(self, amount=1):
        self.data[self._current_labels] -= amount

class FakeSpan:
    def __init__(self, name):
        self.name = name
        self.attributes = {}
        self.status = None
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def set_status(self, status):
        self.status = status

    def record_exception(self, exception):
        self.exception = exception

class FakeTracer:
    def __init__(self):
        self.spans: List[FakeSpan] = []

    def start_as_current_span(self, name: str, **kwargs):
        span = FakeSpan(name)
        self.spans.append(span)
        return span
