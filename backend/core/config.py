"""Application configuration loaded from environment variables."""

from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# Resolve .env from project root (one level above backend/)
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """Application settings loaded from .env file."""
    
    # App
    app_name: str = "AI Use Case Manager"
    env: str = "development"
    log_level: str = "INFO"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./data/app.db"
    
    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours
    
    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-3-haiku"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()