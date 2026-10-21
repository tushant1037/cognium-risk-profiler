import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Cognium Risk Profiler"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Debug
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    # Data file locations (fallback to project root if not in backend/data)
    UNIVERSE_PATH: Path = (
        BASE_DIR / "data" / "universe.json"
        if (BASE_DIR / "data" / "universe.json").exists()
        else ROOT_DIR / "universe.json"
    )
    SNAPSHOT_PATH: Path = (
        BASE_DIR / "data" / "snapshot.json"
        if (BASE_DIR / "data" / "snapshot.json").exists()
        else ROOT_DIR / "snapshot.json"
    )
    
    # Storage for local audit records
    LOCAL_STORAGE_DIR: Path = BASE_DIR / "storage"
    
    # Market Data
    YFINANCE_TIMEOUT_SECONDS: int = 5
    ENABLE_LIVE_YFINANCE: bool = True
    MARKET_DATA_CACHE_TTL_SECONDS: int = 3600
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }

settings = Settings()

# Ensure local storage directory exists
os.makedirs(settings.LOCAL_STORAGE_DIR, exist_ok=True)
