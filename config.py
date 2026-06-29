"""
Application configuration management.
Uses Pydantic Settings for type-safe environment variables.
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./attendance.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    ANOMALY_THRESHOLD: float = 12.0
    MAX_HOURS_PER_DAY: float = 24.0
    MIN_HOURS_PER_DAY: float = 0.0
    TOP_EMPLOYEES_LIMIT: int = 5
    
    # CORS (for frontend integration)
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # File upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set[str] = {".csv"}
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()