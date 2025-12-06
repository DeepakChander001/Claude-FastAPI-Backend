import json
import logging
import os
from datetime import datetime, timezone
from src.app.schemas.security import RequestAudit
from src.app.config import Settings

logger = logging.getLogger(__name__)

def audit_event(event: RequestAudit, settings: Settings = Settings()):
    """
    Writes an audit event to the log file.
    """
    try:
        # Ensure directory exists
        log_path = settings.AUDIT_LOG_PATH
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        entry = event.model_dump()
        # Serialize datetime
        entry["timestamp"] = event.timestamp.isoformat()
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            
    except Exception as e:
        # Fallback logging if file write fails
        logger.error(f"Failed to write audit log: {e}")
