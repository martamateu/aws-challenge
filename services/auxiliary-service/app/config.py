"""Configuration management for Auxiliary Service."""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # App Info
    app_name: str = "Auxiliary Service"
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # AWS Configuration
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_account_id: str = os.getenv("AWS_ACCOUNT_ID", "")
    
    # When running in EKS with IRSA, boto3 will automatically use the service account token
    # No need to configure credentials explicitly
    
    # API Configuration
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
