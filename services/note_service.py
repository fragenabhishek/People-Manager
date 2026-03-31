"""
Note service - handles interaction notes business logic
"""
from datetime import datetime
from typing import List, Optional

from models.note import NOTE_TYPES, Note
from repositories.note_repository import NoteRepository
from repositories.person_repository import PersonRepository
from utils.logger import get_logger
from utils.validators import ValidationError

logger = get_logger(__name__)


class NoteService:
    """Encapsulates all note-related business logic"""

    def __init__(self, note_repository: NoteRepository, person_repository: PersonRepository):
        self.note_repository = note_repository
        self.person_repository = person_repository

    def get_notes_for_person(self, person_id: str, user_id: str) -> List[Note]:
        person = self.person_repository.find_by_id(person_id)
        if not person or person.user_id != user_id:
            return []
        return self.note_repository.find_by_person(person_id, user_id)

    def create_note(self, person_id: str, user_id: str, content: str, note_type: str = 'general') -> Note:
        if not content or not content.strip():
            raise ValidationError("Note content is required")
        if note_type not in NOTE_TYPES:
            raise ValidationError(f"Invalid note type. Must be one of: {', '.join(NOTE_TYPES)}")

        person = self.person_repository.find_by_id(person_id)
        if not person or person.user_id != user_id:
            raise ValidationError("Person not found")

        note = Note(
            person_id=person_id,
            user_id=user_id,
            content=content.strip(),
            note_type=note_type,
        )
        created = self.note_repository.create(note)

        person.last_interaction_at = created.created_at
        person.interaction_count = self.note_repository.count_by_person(person_id)
        self.person_repository.update(person_id, person)

        logger.info(f"Note created for person {person_id} (type: {note_type})")
        return created

    def delete_note(self, note_id: str, user_id: str) -> bool:
        note = self.note_repository.find_by_id(note_id)
        if not note or note.user_id != user_id:
            return False
        success = self.note_repository.delete(note_id)
        if success:
            logger.info(f"Note deleted (ID: {note_id})")
        return success

    def get_recent_activity(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get recent notes across all contacts for activity feed"""
        notes = self.note_repository.find_all({'user_id': user_id})
        notes = sorted(notes, key=lambda n: n.created_at, reverse=True)[:limit]

        activity = []
        for note in notes:
            person = self.person_repository.find_by_id(note.person_id)
            activity.append({
                'note': note.to_dict(),
                'person_name': person.name if person else 'Unknown',
                'person_id': note.person_id,
            })
        return activity
