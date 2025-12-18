from functools import lru_cache
from typing import Optional, Any
from fastapi import Depends
from src.app.config import Settings
from src.app.services.anthropic_client import AnthropicClientProtocol, RealAnthropicClient, MockAnthropicClient
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
    
    # OpenRouter Provider (DeepSeek)
    if settings.OPENROUTER_API_KEY:
        return RealAnthropicClient(
            api_key=settings.OPENROUTER_API_KEY, 
            base_url="https://openrouter.ai/api/v1"
        )

    # Z.AI Provider
    if settings.ZAI_API_KEY:
        return RealAnthropicClient(
            api_key=settings.ZAI_API_KEY, 
            base_url="https://api.z.ai/api/anthropic"
        )

    # Fallback to mock if no key provided
    return MockAnthropicClient()
