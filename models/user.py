"""
User model/entity
Represents a user in the system
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User entity"""

    username: str
    password_hash: str
    id: Optional[str] = None
    email: Optional[str] = None
    mfa_secret: Optional[str] = None
    mfa_enabled: bool = False
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'email': self.email,
            'mfa_secret': self.mfa_secret,
            'mfa_enabled': self.mfa_enabled,
            'is_active': self.is_active,
            'created_at': self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> 'User':
        return User(
            id=data.get('id') or data.get('_id'),
            username=data['username'],
            password_hash=data['password_hash'],
            email=data.get('email'),
            mfa_secret=data.get('mfa_secret'),
            mfa_enabled=data.get('mfa_enabled', False),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at', datetime.now().isoformat()),
        )

    def to_safe_dict(self) -> dict:
        """Return user data without sensitive information."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'mfa_enabled': self.mfa_enabled,
            'created_at': self.created_at,
        }
