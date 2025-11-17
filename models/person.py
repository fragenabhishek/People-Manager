"""
Person model/entity
Represents a person/contact in the system
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Person:
    """Person entity with validation"""
    
    name: str
    user_id: str
    id: Optional[str] = None
    details: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert person to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'details': self.details,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Person':
        """Create Person instance from dictionary"""
        return Person(
            id=data.get('id') or data.get('_id'),
            user_id=data.get('user_id', 'legacy'),  # Handle old data without user_id
            name=data['name'],
            details=data.get('details', ''),
            created_at=data.get('createdAt') or data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updatedAt') or data.get('updated_at', datetime.now().isoformat())
        )
    
    def update(self, name: Optional[str] = None, details: Optional[str] = None) -> None:
        """Update person fields"""
        if name is not None:
            self.name = name
        if details is not None:
            self.details = details
        self.updated_at = datetime.now().isoformat()

