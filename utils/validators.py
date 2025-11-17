"""
Input validation module
Centralizes all validation logic following Single Responsibility Principle
"""
from typing import Dict, List, Optional, Any
import re


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Validator:
    """Input validation utility class"""
    
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> None:
        """
        Validate that a field is not empty
        
        Args:
            value: Value to validate
            field_name: Name of the field for error messages
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"{field_name} is required")
    
    @staticmethod
    def validate_min_length(value: str, min_length: int, field_name: str) -> None:
        """
        Validate minimum string length
        
        Args:
            value: String to validate
            min_length: Minimum required length
            field_name: Name of the field for error messages
            
        Raises:
            ValidationError: If validation fails
        """
        if len(value) < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters"
            )
    
    @staticmethod
    def validate_max_length(value: str, max_length: int, field_name: str) -> None:
        """Validate maximum string length"""
        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} must not exceed {max_length} characters"
            )
    
    @staticmethod
    def validate_email(email: str) -> None:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Raises:
            ValidationError: If email format is invalid
        """
        if email and not Validator.EMAIL_REGEX.match(email):
            raise ValidationError("Invalid email format")
    
    @staticmethod
    def validate_password_match(password: str, confirm_password: str) -> None:
        """
        Validate that passwords match
        
        Args:
            password: Password
            confirm_password: Confirmation password
            
        Raises:
            ValidationError: If passwords don't match
        """
        if password != confirm_password:
            raise ValidationError("Passwords do not match")
    
    @classmethod
    def validate_user_registration(
        cls,
        username: str,
        password: str,
        confirm_password: str,
        email: Optional[str] = None,
        min_username_length: int = 3,
        min_password_length: int = 6
    ) -> None:
        """
        Validate user registration data
        
        Args:
            username: Username
            password: Password
            confirm_password: Password confirmation
            email: Optional email
            min_username_length: Minimum username length
            min_password_length: Minimum password length
            
        Raises:
            ValidationError: If any validation fails
        """
        cls.validate_required(username, "Username")
        cls.validate_required(password, "Password")
        cls.validate_min_length(username, min_username_length, "Username")
        cls.validate_min_length(password, min_password_length, "Password")
        cls.validate_password_match(password, confirm_password)
        
        if email:
            cls.validate_email(email)
    
    @classmethod
    def validate_person_data(cls, name: str, details: Optional[str] = None) -> None:
        """
        Validate person data
        
        Args:
            name: Person name
            details: Optional details
            
        Raises:
            ValidationError: If validation fails
        """
        cls.validate_required(name, "Name")
        cls.validate_min_length(name.strip(), 1, "Name")
        cls.validate_max_length(name.strip(), 200, "Name")
        
        if details and len(details) > 50000:
            raise ValidationError("Details are too long (max 50,000 characters)")

