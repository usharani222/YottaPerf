import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PROJECT_NAME: str = "YottaPerf Performance Management Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "yottaperf-super-secret-key-20261022-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://yotta_user:yotta_password@localhost:5434/yottaperf_db"
    )
    
    # Deterministic generation defaults
    DEFAULT_SEED: int = 20261022
    REFERENCE_DATE: str = "2026-06-30"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "*"
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def __init__(self, **values):
        super().__init__(**values)
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY or "change-in-production" in self.SECRET_KEY:
                raise ValueError(
                    "FATAL SECURITY VIOLATION: Insecure default SECRET_KEY detected in production environment! "
                    "A secure, cryptographically random SECRET_KEY must be configured via environment variable."
                )


settings = Settings()

