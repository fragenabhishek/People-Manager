"""
Note model/entity
Represents an interaction note attached to a person
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


NOTE_TYPES = ('general', 'meeting', 'call', 'email', 'event', 'follow_up')


@dataclass
class Note:
    """Interaction note entity"""

    person_id: str
    user_id: str
    content: str
    note_type: str = "general"
    id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'person_id': self.person_id,
            'user_id': self.user_id,
            'content': self.content,
            'note_type': self.note_type,
            'created_at': self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> 'Note':
        return Note(
            id=data.get('id') or data.get('_id'),
            person_id=data['person_id'],
            user_id=data['user_id'],
            content=data['content'],
            note_type=data.get('note_type', 'general'),
            created_at=data.get('created_at', datetime.now().isoformat()),
        )
