"""Configuration management for Main API."""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # App Info
    app_name: str = "Main API"
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Auxiliary Service
    auxiliary_service_url: str = os.getenv(
        "AUXILIARY_SERVICE_URL", 
        "http://auxiliary-service.auxiliary-service.svc.cluster.local:8001"
    )
    auxiliary_service_timeout: int = 30
    
    # API Configuration
    api_prefix: str = "/api/v1"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS
    cors_origins: list = ["*"]
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
