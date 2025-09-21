"""
Configuration settings for the Edix application.
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "Edix"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    WORKERS: int = 1
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Default React dev server
        "http://localhost:8000",  # Default FastAPI server
    ]
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./edix.db"
    TEST_DATABASE_URL: str = "sqlite:///./test_edix.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # WebSocket settings
    WS_PREFIX: str = "/ws"
    WS_URL: Optional[str] = None
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # File storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Frontend settings
    FRONTEND_DIR: str = str(Path(__file__).parent.parent / "frontend_src")
    STATIC_DIR: str = str(Path(__file__).parent / "static")
    TEMPLATES_DIR: str = str(Path(__file__).parent / "templates")
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @field_validator("WS_URL", mode="before")
    @classmethod
    def assemble_ws_url(cls, v: Optional[str], info) -> str:
        if v:
            return v
        # Default to the same host as the API
        values = info.data if hasattr(info, 'data') else {}
        host = values.get("HOST", "localhost")
        port = values.get("PORT", 8000)
        ws_protocol = "wss" if values.get("HTTPS", False) else "ws"
        return f"{ws_protocol}://{host}:{port}{values.get('WS_PREFIX', '/ws')}"
    
    @property
    def database_url_async(self) -> str:
        """Get the async database URL."""
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
        return self.DATABASE_URL
    
    @property
    def test_database_url_async(self) -> str:
        """Get the async test database URL."""
        if self.TEST_DATABASE_URL.startswith("sqlite"):
            return self.TEST_DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
        return self.TEST_DATABASE_URL


# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
