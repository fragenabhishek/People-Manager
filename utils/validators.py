"""
Input validation module
Centralizes all validation logic
"""
from typing import Optional, Any
import re


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Validator:
    """Input validation utility class"""

    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    URL_REGEX = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)

    @staticmethod
    def validate_required(value: Any, field_name: str) -> None:
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"{field_name} is required")

    @staticmethod
    def validate_min_length(value: str, min_length: int, field_name: str) -> None:
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters")

    @staticmethod
    def validate_max_length(value: str, max_length: int, field_name: str) -> None:
        if len(value) > max_length:
            raise ValidationError(f"{field_name} must not exceed {max_length} characters")

    @staticmethod
    def validate_email(email: str) -> None:
        if email and not Validator.EMAIL_REGEX.match(email):
            raise ValidationError("Invalid email format")

    @staticmethod
    def validate_url(url: str, field_name: str = "URL") -> None:
        if url and not Validator.URL_REGEX.match(url):
            raise ValidationError(f"Invalid {field_name} format")

    @staticmethod
    def validate_password_match(password: str, confirm_password: str) -> None:
        if password != confirm_password:
            raise ValidationError("Passwords do not match")

    @classmethod
    def validate_user_registration(
        cls, username: str, password: str, confirm_password: str,
        email: Optional[str] = None, min_username_length: int = 3,
        min_password_length: int = 6,
    ) -> None:
        cls.validate_required(username, "Username")
        cls.validate_required(password, "Password")
        cls.validate_min_length(username, min_username_length, "Username")
        cls.validate_min_length(password, min_password_length, "Password")
        cls.validate_password_match(password, confirm_password)
        if email:
            cls.validate_email(email)

    @classmethod
    def validate_person_data(cls, name: str, details: Optional[str] = None) -> None:
        cls.validate_required(name, "Name")
        cls.validate_min_length(name.strip(), 1, "Name")
        cls.validate_max_length(name.strip(), 200, "Name")
        if details and len(details) > 50000:
            raise ValidationError("Details are too long (max 50,000 characters)")

    @classmethod
    def validate_date(cls, date_str: str, field_name: str = "Date") -> None:
        """Validate date format YYYY-MM-DD"""
        if not date_str:
            return
        date_regex = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not date_regex.match(date_str):
            raise ValidationError(f"{field_name} must be in YYYY-MM-DD format")
