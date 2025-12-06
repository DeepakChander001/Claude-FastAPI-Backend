import re
from typing import Dict, Any, List, Optional

# Common patterns to redact
PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "API_KEY": r"(sk-[a-zA-Z0-9]{20,})", # Example pattern for API keys
    "JWT": r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b"
}

def redact_text(text: str, patterns: Optional[List[str]] = None) -> str:
    """
    Redacts sensitive information from text using regex patterns.
    """
    if not text:
        return text
        
    if patterns is None:
        patterns = list(PATTERNS.values())
        
    redacted_text = text
    for pattern in patterns:
        redacted_text = re.sub(pattern, "[REDACTED]", redacted_text)
        
    return redacted_text

def redact_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redacts sensitive headers like Authorization, X-API-Key.
    Returns a new dictionary.
    """
    SENSITIVE_HEADERS = {"authorization", "x-api-key", "cookie", "set-cookie"}
    
    redacted = {}
    for k, v in headers.items():
        if k.lower() in SENSITIVE_HEADERS:
            redacted[k] = "[REDACTED]"
        else:
            redacted[k] = v
            
    return redacted
