from functools import lru_cache
from fastapi import Depends
from src.app.config import Settings
from src.app.client import AnthropicClientWrapper

@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the application settings.
    """
    return Settings()

def get_client(settings: Settings = Depends(get_settings)) -> AnthropicClientWrapper:
    """
    Dependency that provides an instance of AnthropicClientWrapper.
    """
    return AnthropicClientWrapper(api_key=settings.ANTHROPIC_API_KEY)
