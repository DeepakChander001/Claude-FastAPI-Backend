import logging
import json
from fastapi import APIRouter, Request, Response, Depends
from pydantic import BaseModel
from src.app.config import Settings
from src.app.dependencies import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/security/csp-report")
async def csp_report_endpoint(request: Request, settings: Settings = Depends(get_settings)):
    """
    Receives CSP violation reports.
    Always returns 204 to avoid blocking the browser.
    """
    try:
        # CSP reports are sent as application/csp-report or application/json
        # We try to parse JSON body
        body = await request.body()
        if not body:
            return Response(status_code=204)
            
        report_data = json.loads(body)
        
        # Log structured report
        logger.warning(
            "CSP Violation Reported",
            extra={
                "extra_data": {
                    "csp_report": report_data.get("csp-report", {}),
                    "type": "security_violation"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to process CSP report: {e}")
        
    return Response(status_code=204)
