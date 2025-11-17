"""
Configuration management module
Centralizes all configuration settings with proper validation
"""
import os
from typing import Optional


class Config:
    """Application configuration with environment variable support"""
    
    # Flask Configuration
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Configuration
    MONGO_URI: Optional[str] = os.environ.get('MONGO_URI')
    USE_MONGODB: bool = MONGO_URI is not None
    DATA_FILE: str = 'data.json'
    USERS_FILE: str = 'users.json'
    
    # Database Collection Names
    DB_NAME: str = 'people_manager'
    PEOPLE_COLLECTION: str = 'people'
    USERS_COLLECTION: str = 'users'
    
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
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings"""
        if cls.DEBUG and cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            print("⚠️  WARNING: Using default secret key in development mode")
        
        if cls.USE_MONGODB:
            print(f"✓ MongoDB enabled: {cls.DB_NAME}")
        else:
            print(f"✓ Using local file storage: {cls.DATA_FILE}")
        
        if cls.AI_ENABLED:
            print(f"✓ AI features enabled: {cls.GEMINI_MODEL}")
        else:
            print("⚠️  AI features disabled: GEMINI_API_KEY not set")

