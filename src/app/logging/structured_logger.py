import logging
import json
import datetime
import threading
import queue
import sys
from typing import Any, Dict, Optional
from src.app.logging.redaction import redact_text

# Global queue for non-blocking logging
_LOG_QUEUE = queue.Queue(maxsize=1000)
_LISTENER_THREAD = None

class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        """
        Formats log record as JSON.
        """
        log_record = {
            "ts": datetime.datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "service": "claude-proxy",
            "name": record.name,
            "message": redact_text(record.getMessage()),
            "file": record.filename,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "trace_id"):
            log_record["trace_id"] = record.trace_id
        if hasattr(record, "span_id"):
            log_record["span_id"] = record.span_id
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if hasattr(record, "route"):
            log_record["route"] = record.route
        if hasattr(record, "latency_ms"):
            log_record["latency_ms"] = record.latency_ms
        if hasattr(record, "status"):
            log_record["status"] = record.status
            
        # Merge 'extra' dict if passed
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        return json.dumps(log_record)

def _log_listener():
    """
    Background thread to process log records from queue.
    """
    while True:
        try:
            record = _LOG_QUEUE.get()
            if record is None:
                break
            # In a real app, this would write to a file or network socket.
            # Here we just print to stderr/stdout to avoid blocking main loop IO
            # if we were writing to a slow disk/network.
            # For standard logging, we might re-emit to a handler.
            # But to keep it simple and safe, we just let the handler do the work
            # and this queue is just a buffer if we were using a QueueHandler.
            # Actually, Python's QueueHandler/QueueListener pattern is better.
            # Let's implement a simple QueueHandler that puts into _LOG_QUEUE
            # and a listener that writes to StreamHandler.
            pass 
        except Exception:
            pass

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

def configure_logging(env: str = "dev", log_level: str = "INFO", json_format: bool = True):
    """
    Configures the root logger.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    handler = logging.StreamHandler(sys.stdout)
    
    if json_format:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
    root_logger.addHandler(handler)
    
    # Guidance for Production:
    # if env == "production":
    #     # Use Watchtower for CloudWatch
    #     # from watchtower import CloudWatchLogHandler
    #     # root_logger.addHandler(CloudWatchLogHandler())
    #     pass

class LoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = self.extra.copy()
        if 'extra' in kwargs:
            extra.update(kwargs.pop('extra'))
        kwargs['extra'] = extra
        return msg, kwargs

def bind_logger(logger: logging.Logger, **kwargs) -> logging.LoggerAdapter:
    return LoggerAdapter(logger, kwargs)
