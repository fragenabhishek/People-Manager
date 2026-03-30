"""
Configuration management module
Centralizes all configuration settings with proper validation
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration with environment variable support"""

    # Flask Configuration
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database Configuration
    MONGO_URI: Optional[str] = os.environ.get('MONGO_URI')
    USE_MONGODB: bool = MONGO_URI is not None
    DATA_FILE: str = 'data.json'
    USERS_FILE: str = 'users.json'
    NOTES_FILE: str = 'notes.json'

    # Database Collection Names
    DB_NAME: str = 'people_manager'
    PEOPLE_COLLECTION: str = 'people'
    USERS_COLLECTION: str = 'users'
    NOTES_COLLECTION: str = 'notes'

    # AI Configuration
    GEMINI_API_KEY: Optional[str] = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL: str = 'gemini-2.5-flash'
    AI_ENABLED: bool = GEMINI_API_KEY is not None

    # Server Configuration
    HOST: str = '0.0.0.0'
    PORT: int = int(os.environ.get('PORT', 5000))
    DEBUG: bool = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Security Configuration
    PASSWORD_MIN_LENGTH: int = 6
    USERNAME_MIN_LENGTH: int = 3
    SESSION_PERMANENT: bool = False
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'
    WTF_CSRF_ENABLED: bool = True

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "200 per day"
    RATE_LIMIT_LOGIN: str = "10 per minute"
    RATE_LIMIT_API: str = "60 per minute"
    RATE_LIMIT_AI: str = "20 per minute"

    # Relationship Scoring Thresholds (days)
    RELATIONSHIP_WARM_DAYS: int = 14
    RELATIONSHIP_LUKEWARM_DAYS: int = 30
    # Anything beyond LUKEWARM_DAYS is considered "cold"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Import/Export
    MAX_IMPORT_ROWS: int = 5000
    EXPORT_DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings"""
        if cls.DEBUG and cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            print("WARNING: Using default secret key in development mode")

        if cls.USE_MONGODB:
            print(f"MongoDB enabled: {cls.DB_NAME}")
        else:
            print(f"Using local file storage: {cls.DATA_FILE}")

        if cls.AI_ENABLED:
            print(f"AI features enabled: {cls.GEMINI_MODEL}")
        else:
            print("AI features disabled: GEMINI_API_KEY not set")
