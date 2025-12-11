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
    CLAUDE_SESSION_KEY: Optional[str] = None  # Unofficial Web Session Key
    CLAUDE_WEB_ENABLED: bool = False # Toggle to use Web Client instead of API
    USE_MOCK_CLIENT: bool = True
    DEFAULT_MODEL: str = "claude-3-haiku-20240307"
    
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

    # Security Configuration
    AUTH_MODE: str = "api_key"  # api_key, jwt, none
    ALLOWED_API_KEYS: str = ""  # Comma separated list
    JWT_SECRET: str = "REPLACE_ME"
    RATE_LIMIT_PER_MINUTE: int = 60
    AUDIT_LOG_PATH: str = "logs/audit.log"

    # Queue Configuration
    QUEUE_MAX_ATTEMPTS: int = 3
    QUEUE_DLQ_NAME: str = "dead_letter_queue"

    # Observability Configuration
    ENABLE_TRACING: bool = False
    LOG_JSON: bool = True
    TRACE_SAMPLING_RATE: float = 1.0

    # Security Hardening
    CSP_REPORT_ONLY: bool = True
    HSTS_MAX_AGE: int = 31536000
    SEC_SCAN_FAIL_ON_HIGH: bool = False

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
            if "ANTHROPIC_API_KEY" in secrets:
                self.ANTHROPIC_API_KEY = secrets["ANTHROPIC_API_KEY"]
            if "CLAUDE_SESSION_KEY" in secrets:
                self.CLAUDE_SESSION_KEY = secrets["CLAUDE_SESSION_KEY"]
            if "SUPABASE_URL" in secrets:
                self.SUPABASE_URL = secrets["SUPABASE_URL"]
            if "SUPABASE_KEY" in secrets:
                self.SUPABASE_KEY = secrets["SUPABASE_KEY"]
            
            # Security Secrets
            if "ALLOWED_API_KEYS" in secrets:
                self.ALLOWED_API_KEYS = secrets["ALLOWED_API_KEYS"]
            if "JWT_SECRET" in secrets:
                self.JWT_SECRET = secrets["JWT_SECRET"]
