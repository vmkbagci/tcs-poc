"""Configuration management for different environments."""

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_prefix="TRADE_API_"
    )
    
    # Application settings
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000
    
    # API settings
    api_title: str = "Trade API"
    api_version: str = "0.1.0"
    
    # Trade store settings
    max_trades_in_memory: int = 10000


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()