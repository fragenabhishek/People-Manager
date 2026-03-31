"""
Person model/entity
Represents a person/contact in the system with structured fields
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Person:
    """Person entity with structured contact fields"""

    name: str
    user_id: str
    id: Optional[str] = None

    # Structured contact fields
    email: str = ""
    phone: str = ""
    company: str = ""
    job_title: str = ""
    location: str = ""
    linkedin_url: str = ""
    twitter_handle: str = ""
    website: str = ""

    # Rich details
    details: str = ""
    how_we_met: str = ""
    profile_image_url: str = ""

    # Dates
    birthday: str = ""
    anniversary: str = ""
    met_at: str = ""

    # Organization
    tags: List[str] = field(default_factory=list)

    # Follow-up
    next_follow_up: str = ""
    follow_up_frequency_days: int = 0

    # Relationship scoring (auto-calculated)
    relationship_score: float = 0.0
    relationship_status: str = "new"  # new, warm, lukewarm, cold
    last_interaction_at: str = ""
    interaction_count: int = 0

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert person to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'job_title': self.job_title,
            'location': self.location,
            'linkedin_url': self.linkedin_url,
            'twitter_handle': self.twitter_handle,
            'website': self.website,
            'details': self.details,
            'how_we_met': self.how_we_met,
            'profile_image_url': self.profile_image_url,
            'birthday': self.birthday,
            'anniversary': self.anniversary,
            'met_at': self.met_at,
            'tags': self.tags,
            'next_follow_up': self.next_follow_up,
            'follow_up_frequency_days': self.follow_up_frequency_days,
            'relationship_score': self.relationship_score,
            'relationship_status': self.relationship_status,
            'last_interaction_at': self.last_interaction_at,
            'interaction_count': self.interaction_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @staticmethod
    def from_dict(data: dict) -> 'Person':
        """Create Person instance from dictionary (backward-compatible)"""
        return Person(
            id=data.get('id') or data.get('_id'),
            user_id=data.get('user_id', 'legacy'),
            name=data['name'],
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            company=data.get('company', ''),
            job_title=data.get('job_title', ''),
            location=data.get('location', ''),
            linkedin_url=data.get('linkedin_url', ''),
            twitter_handle=data.get('twitter_handle', ''),
            website=data.get('website', ''),
            details=data.get('details', ''),
            how_we_met=data.get('how_we_met', ''),
            profile_image_url=data.get('profile_image_url', ''),
            birthday=data.get('birthday', ''),
            anniversary=data.get('anniversary', ''),
            met_at=data.get('met_at', ''),
            tags=data.get('tags', []),
            next_follow_up=data.get('next_follow_up', ''),
            follow_up_frequency_days=data.get('follow_up_frequency_days', 0),
            relationship_score=data.get('relationship_score', 0.0),
            relationship_status=data.get('relationship_status', 'new'),
            last_interaction_at=data.get('last_interaction_at', ''),
            interaction_count=data.get('interaction_count', 0),
            created_at=data.get('created_at') or data.get('createdAt', datetime.now().isoformat()),
            updated_at=data.get('updated_at') or data.get('updatedAt', datetime.now().isoformat()),
        )

    def update(self, **kwargs) -> None:
        """Update person fields dynamically"""
        for key, value in kwargs.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
