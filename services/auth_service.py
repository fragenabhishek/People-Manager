"""
Authentication service
Handles user authentication and registration logic
Single Responsibility: Authentication and user management
"""
from typing import Optional
from flask_bcrypt import Bcrypt

from models.user import User
from repositories.user_repository import UserRepository
from utils.validators import Validator, ValidationError
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)


class AuthService:
    """
    Authentication service
    Encapsulates all authentication-related business logic
    """
    
    def __init__(self, user_repository: UserRepository, bcrypt: Bcrypt):
        """
        Initialize auth service with dependencies
        
        Args:
            user_repository: User repository for data access
            bcrypt: Bcrypt instance for password hashing
        """
        self.user_repository = user_repository
        self.bcrypt = bcrypt
    
    def register_user(
        self,
        username: str,
        password: str,
        confirm_password: str,
        email: Optional[str] = None
    ) -> User:
        """
        Register a new user
        
        Args:
            username: User's username
            password: User's password
            confirm_password: Password confirmation
            email: Optional email address
            
        Returns:
            Created User entity
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate input
        try:
            Validator.validate_user_registration(
                username=username.strip(),
                password=password,
                confirm_password=confirm_password,
                email=email.strip() if email else None,
                min_username_length=Config.USERNAME_MIN_LENGTH,
                min_password_length=Config.PASSWORD_MIN_LENGTH
            )
        except ValidationError as e:
            logger.warning(f"User registration validation failed: {e}")
            raise
        
        # Check if username already exists
        if self.user_repository.find_by_username(username.strip()):
            logger.warning(f"Registration attempt with existing username: {username}")
            raise ValidationError("Username already exists")
        
        # Create user
        password_hash = self.bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            username=username.strip(),
            password_hash=password_hash,
            email=email.strip() if email else None
        )
        
        created_user = self.user_repository.create(user)
        logger.info(f"User registered successfully: {created_user.username}")
        return created_user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            User entity if authentication successful, None otherwise
        """
        # Validate input
        try:
            Validator.validate_required(username, "Username")
            Validator.validate_required(password, "Password")
        except ValidationError as e:
            logger.warning(f"Authentication validation failed: {e}")
            return None
        
        # Find user
        user = self.user_repository.find_by_username(username.strip())
        
        if not user:
            logger.warning(f"Authentication failed: user not found - {username}")
            return None
        
        # Verify password
        if not self.bcrypt.check_password_hash(user.password_hash, password):
            logger.warning(f"Authentication failed: invalid password - {username}")
            return None
        
        logger.info(f"User authenticated successfully: {username}")
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.user_repository.find_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.user_repository.find_by_username(username)

