"""
User model/entity
Represents a user in the system
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User entity with validation"""
    
    username: str
    password_hash: str
    id: Optional[str] = None
    email: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'email': self.email,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'User':
        """Create User instance from dictionary"""
        return User(
            id=data.get('id') or data.get('_id'),
            username=data['username'],
            password_hash=data['password_hash'],
            email=data.get('email'),
            created_at=data.get('created_at', datetime.now().isoformat())
        )
    
    def to_safe_dict(self) -> dict:
        """Return user data without sensitive information"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at
        }

