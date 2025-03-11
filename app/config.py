# app/config.py
"""Application configuration settings."""
import os
import logging
from pydantic_settings import BaseSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings
    db_url: str = os.getenv("DB_URL", "sqlite+aiosqlite:///data/phone_calls.db")
    
    # Server settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    # Application name
    app_name: str = "Phone Call Logger"


# Create settings instance
settings = Settings()

