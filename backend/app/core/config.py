from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "SignBridge AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "signbridge-secret-key-change-in-production-2026-secure-jwt"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database (Default: SQLite async for zero-config local dev, override with PostgreSQL in production)
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/signbridge.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]
    
    # Machine Learning Settings
    CONFIDENCE_THRESHOLD: float = 0.65
    SMOOTHING_WINDOW: int = 5
    SEQUENCE_BUFFER_LENGTH: int = 20
    
    # Paths to models
    LEGACY_MODEL_PATH: str = str(BASE_DIR.parent / "Final Project" / "Source Code" / "cnn8grps_rad1_model.h5")
    DYNAMIC_MODEL_PATH: str = str(BASE_DIR.parent.parent / "majorproject_new" / "Sign-Language-AI" / "action_model.h5")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
