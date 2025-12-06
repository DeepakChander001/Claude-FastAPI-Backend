import pytest
from src.app.logging.redaction import redact_text, redact_headers

def test_redact_text_email():
    text = "Contact me at user@example.com for info."
    redacted = redact_text(text)
    assert "user@example.com" not in redacted
    assert "[REDACTED]" in redacted

def test_redact_text_api_key():
    text = "My key is sk-1234567890abcdef1234567890abcdef."
    redacted = redact_text(text)
    assert "sk-1234567890" not in redacted
    assert "[REDACTED]" in redacted

def test_redact_headers():
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer secret-token",
        "X-API-Key": "sk-secret"
    }
    redacted = redact_headers(headers)
    assert redacted["Content-Type"] == "application/json"
    assert redacted["Authorization"] == "[REDACTED]"
    assert redacted["X-API-Key"] == "[REDACTED]"

def test_redact_no_pii():
    text = "Hello world"
    assert redact_text(text) == "Hello world"
