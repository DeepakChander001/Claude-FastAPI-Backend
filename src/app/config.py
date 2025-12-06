import os
import logging
from typing import Optional, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.app.aws_secrets import get_secrets_from_aws

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and optionally AWS Secrets Manager.
    """
    ANTHROPIC_API_KEY: Optional[str] = None
    USE_MOCK_CLIENT: bool = True
    DEFAULT_MODEL: str = "claude-3.5"
    
    # AWS Secrets Manager Configuration
    AWS_SECRETS_MANAGER_ENABLED: bool = False
    AWS_SECRETS_NAME: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Database (Legacy/Fallback)
    DATABASE_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def load_from_aws_secrets(self, boto3_client: Optional[Any] = None) -> None:
        """
        If AWS Secrets Manager is enabled, fetches secrets and updates settings.
        
        Args:
            boto3_client: Optional mock client for testing.
        """
        if self.AWS_SECRETS_MANAGER_ENABLED and self.AWS_SECRETS_NAME:
            logger.info(f"Fetching secrets from AWS Secrets Manager: {self.AWS_SECRETS_NAME}")
            secrets = get_secrets_from_aws(self.AWS_SECRETS_NAME, boto3_client)
            
            # Update settings if keys exist in the secret
            # Example secret JSON:
            # {
            #   "ANTHROPIC_API_KEY": "sk-...",
            #   "SUPABASE_URL": "https://...",
            #   "SUPABASE_KEY": "eyJ..."
            # }
            
            if "ANTHROPIC_API_KEY" in secrets:
                self.ANTHROPIC_API_KEY = secrets["ANTHROPIC_API_KEY"]
            if "SUPABASE_URL" in secrets:
                self.SUPABASE_URL = secrets["SUPABASE_URL"]
            if "SUPABASE_KEY" in secrets:
                self.SUPABASE_KEY = secrets["SUPABASE_KEY"]
            
            # Add other fields as needed
