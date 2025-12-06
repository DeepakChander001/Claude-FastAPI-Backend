import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    In production, secrets should be managed via AWS Secrets Manager.
    """
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "claude-3.5")

    class Config:
        env_file = ".env"
