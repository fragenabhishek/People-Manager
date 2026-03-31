"""
Authentication service
Handles user authentication, registration, and password management.
"""
from typing import Optional

from flask_bcrypt import Bcrypt

from config import Config
from models.user import User
from repositories.user_repository import UserRepository
from utils.logger import get_logger
from utils.validators import ValidationError, Validator

logger = get_logger(__name__)


class AuthService:

    def __init__(self, user_repository: UserRepository, bcrypt: Bcrypt):
        self.user_repository = user_repository
        self.bcrypt = bcrypt

    def register_user(
        self,
        username: str,
        password: str,
        confirm_password: str,
        email: Optional[str] = None,
    ) -> User:
        try:
            Validator.validate_user_registration(
                username=username.strip(),
                password=password,
                confirm_password=confirm_password,
                email=email.strip() if email else None,
                min_username_length=Config.USERNAME_MIN_LENGTH,
                min_password_length=Config.PASSWORD_MIN_LENGTH,
            )
        except ValidationError:
            raise

        if self.user_repository.find_by_username(username.strip()):
            raise ValidationError("Username already exists")

        password_hash = self.bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            username=username.strip(),
            password_hash=password_hash,
            email=email.strip() if email else None,
        )

        created_user = self.user_repository.create(user)
        logger.info(f"User registered: {created_user.username}")
        return created_user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        try:
            Validator.validate_required(username, "Username")
            Validator.validate_required(password, "Password")
        except ValidationError:
            return None

        user = self.user_repository.find_by_username(username.strip())
        if not user:
            return None
        if not self.bcrypt.check_password_hash(user.password_hash, password):
            return None

        logger.info(f"User authenticated: {username}")
        return user

    def change_password(self, user_id: str, current_password: str, new_password: str, confirm_password: str) -> bool:
        """Change password for authenticated user."""
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValidationError("User not found")

        if not self.bcrypt.check_password_hash(user.password_hash, current_password):
            raise ValidationError("Current password is incorrect")

        Validator.validate_min_length(new_password, Config.PASSWORD_MIN_LENGTH, "New password")
        Validator.validate_password_match(new_password, confirm_password)

        user.password_hash = self.bcrypt.generate_password_hash(new_password).decode('utf-8')
        self.user_repository.update(user.id, user)
        logger.info(f"Password changed for user {user.username}")
        return True

    def reset_password(self, user_id: str, new_password: str) -> bool:
        """Reset password using a verified reset token (token already validated by caller)."""
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValidationError("User not found")

        Validator.validate_min_length(new_password, Config.PASSWORD_MIN_LENGTH, "New password")

        user.password_hash = self.bcrypt.generate_password_hash(new_password).decode('utf-8')
        self.user_repository.update(user.id, user)
        logger.info(f"Password reset for user {user.username}")
        return True

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.user_repository.find_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.user_repository.find_by_username(username)

    def find_user_by_email(self, email: str) -> Optional[User]:
        """Find user by email address (for password reset)."""
        users = self.user_repository.find_all()
        return next((u for u in users if u.email and u.email.lower() == email.lower()), None)
