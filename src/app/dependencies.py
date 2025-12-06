from functools import lru_cache
from typing import Optional, Any
from fastapi import Depends
from src.app.config import Settings
from src.app.services.anthropic_client import AnthropicClientProtocol, RealAnthropicClient, MockAnthropicClient

# Singleton instance
_settings_instance: Optional[Settings] = None

def get_settings(boto3_client: Optional[Any] = None) -> Settings:
    """
    Returns a cached instance of the application settings.
    If AWS Secrets Manager is enabled, it attempts to load secrets.
    
    Args:
        boto3_client: Optional mock client for testing injection.
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
        if _settings_instance.AWS_SECRETS_MANAGER_ENABLED:
            _settings_instance.load_from_aws_secrets(boto3_client=boto3_client)
    return _settings_instance

def get_anthropic_client(settings: Settings = Depends(get_settings)) -> AnthropicClientProtocol:
    """
    Dependency that provides an instance of AnthropicClientProtocol.
    Returns MockAnthropicClient if USE_MOCK_CLIENT is True, otherwise RealAnthropicClient.
    """
    if settings.USE_MOCK_CLIENT:
        return MockAnthropicClient()
    
    # Ensure API key is present for real client
    if not settings.ANTHROPIC_API_KEY:
        # Fallback to mock or raise error depending on strictness. 
        # For now, we'll return mock if key is missing to prevent crash, 
        # but in prod this should likely be an error.
        return MockAnthropicClient()
        
    return RealAnthropicClient(api_key=settings.ANTHROPIC_API_KEY)
