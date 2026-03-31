"""
Configuration management module
Centralizes all configuration settings with proper validation
"""
import logging
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration with environment variable support"""

    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database — priority: DATABASE_URL (SQL) > MONGO_URI > JSON files
    DATABASE_URL: Optional[str] = os.environ.get('DATABASE_URL')
    USE_SQL: bool = DATABASE_URL is not None
    MONGO_URI: Optional[str] = os.environ.get('MONGO_URI')
    USE_MONGODB: bool = MONGO_URI is not None and DATABASE_URL is None
    DATA_FILE: str = 'data.json'
    USERS_FILE: str = 'users.json'
    NOTES_FILE: str = 'notes.json'

    DB_NAME: str = 'people_manager'
    PEOPLE_COLLECTION: str = 'people'
    USERS_COLLECTION: str = 'users'
    NOTES_COLLECTION: str = 'notes'

    # AI
    GEMINI_API_KEY: Optional[str] = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL: str = 'gemini-2.5-flash'
    AI_ENABLED: bool = GEMINI_API_KEY is not None

    # Server
    HOST: str = '0.0.0.0'
    PORT: int = int(os.environ.get('PORT', 5000))
    DEBUG: bool = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Security
    PASSWORD_MIN_LENGTH: int = 6
    USERNAME_MIN_LENGTH: int = 3
    SESSION_PERMANENT: bool = False
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'
    WTF_CSRF_ENABLED: bool = True

    # JWT
    JWT_ACCESS_TOKEN_MINUTES: int = int(os.environ.get('JWT_ACCESS_TOKEN_MINUTES', 15))
    JWT_REFRESH_TOKEN_MINUTES: int = int(os.environ.get('JWT_REFRESH_TOKEN_MINUTES', 10080))  # 7 days

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "200 per day"
    RATE_LIMIT_LOGIN: str = "10 per minute"
    RATE_LIMIT_API: str = "60 per minute"
    RATE_LIMIT_AI: str = "20 per minute"

    # Relationship Scoring Thresholds (days)
    RELATIONSHIP_WARM_DAYS: int = 14
    RELATIONSHIP_LUKEWARM_DAYS: int = 30

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Import/Export
    MAX_IMPORT_ROWS: int = 5000
    EXPORT_DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    @classmethod
    def validate(cls) -> None:
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            if cls.DEBUG:
                logger.warning("Using default secret key — acceptable only in dev mode")
            else:
                raise RuntimeError(
                    "SECRET_KEY must be set in production. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
                )

        if cls.USE_SQL:
            storage = f"SQL ({cls.DATABASE_URL.split('@')[-1] if '@' in cls.DATABASE_URL else cls.DATABASE_URL})"
        elif cls.USE_MONGODB:
            storage = f"MongoDB ({cls.DB_NAME})"
        else:
            storage = f"Local JSON ({cls.DATA_FILE})"
        logger.info("Storage: %s", storage)
        logger.info("AI: %s", f"enabled ({cls.GEMINI_MODEL})" if cls.AI_ENABLED else "disabled")
