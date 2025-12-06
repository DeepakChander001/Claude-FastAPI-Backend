import pytest
import json
from unittest.mock import MagicMock
from src.app.config import Settings

def test_settings_load_defaults():
    """
    Verify Settings loads values from .env (or defaults) when AWS secrets are disabled.
    """
    settings = Settings(AWS_SECRETS_MANAGER_ENABLED=False)
    assert settings.USE_MOCK_CLIENT is True  # Default
    assert settings.ENVIRONMENT == "development"

def test_load_from_aws_secrets_success():
    """
    Verify load_from_aws_secrets merges values correctly using a mock boto3 client.
    """
    # Mock boto3 client and response
    mock_client = MagicMock()
    secret_payload = {
        "ANTHROPIC_API_KEY": "sk-test-key",
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test-key"
    }
    mock_client.get_secret_value.return_value = {
        "SecretString": json.dumps(secret_payload)
    }

    # Initialize settings with AWS enabled
    settings = Settings(
        AWS_SECRETS_MANAGER_ENABLED=True,
        AWS_SECRETS_NAME="test-secret"
    )
    
    # Load secrets using the mock client
    settings.load_from_aws_secrets(boto3_client=mock_client)
    
    # Assertions
    assert settings.ANTHROPIC_API_KEY == "sk-test-key"
    assert settings.SUPABASE_URL == "https://test.supabase.co"
    assert settings.SUPABASE_KEY == "test-key"
    
    # Verify client call
    mock_client.get_secret_value.assert_called_once_with(SecretId="test-secret")

def test_load_from_aws_secrets_failure_graceful():
    """
    Verify that failure to fetch secrets (e.g., network error) is handled gracefully.
    """
    mock_client = MagicMock()
    mock_client.get_secret_value.side_effect = Exception("Network error")
    
    settings = Settings(
        AWS_SECRETS_MANAGER_ENABLED=True,
        AWS_SECRETS_NAME="test-secret",
        ANTHROPIC_API_KEY="INITIAL_TEST_VALUE"
    )
    
    # Should not raise exception
    settings.load_from_aws_secrets(boto3_client=mock_client)
    
    # Values should remain as initialized
    assert settings.ANTHROPIC_API_KEY == "INITIAL_TEST_VALUE"
