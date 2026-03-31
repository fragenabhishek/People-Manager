"""
SQLAlchemy-backed NoteRepository.
Same interface as the JSON/MongoDB version — services are unaware of the backend.
"""
import uuid
from typing import List, Optional

from models.note import Note
from models.tables import NoteRow
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class SqlNoteRepository(BaseRepository[Note]):

    def __init__(self, session_factory):
        self._sf = session_factory

    # --- conversions ---

    @staticmethod
    def _to_domain(row: NoteRow) -> Note:
        return Note(
            id=row.id,
            person_id=row.person_id,
            user_id=row.user_id,
            content=row.content,
            note_type=row.note_type or "general",
            created_at=row.created_at or "",
        )

    # --- BaseRepository interface ---

    def find_all(self, filters: Optional[dict] = None) -> List[Note]:
        with self._sf() as s:
            q = s.query(NoteRow)
            if filters:
                for k, v in filters.items():
                    q = q.filter(getattr(NoteRow, k) == v)
            q = q.order_by(NoteRow.created_at.desc())
            return [self._to_domain(r) for r in q.all()]

    def find_by_id(self, entity_id: str) -> Optional[Note]:
        with self._sf() as s:
            row = s.get(NoteRow, entity_id)
            return self._to_domain(row) if row else None

    def find_by_person(self, person_id: str, user_id: str) -> List[Note]:
        return self.find_all({"person_id": person_id, "user_id": user_id})

    def create(self, entity: Note) -> Note:
        if not entity.id:
            entity.id = str(uuid.uuid4())
        row = NoteRow(
            id=entity.id,
            person_id=entity.person_id,
            user_id=entity.user_id,
            content=entity.content,
            note_type=entity.note_type,
            created_at=entity.created_at,
        )
        with self._sf() as s:
            s.add(row)
            s.commit()
            s.refresh(row)
            created = self._to_domain(row)
        logger.info(f"Created note (ID: {created.id}) for person {created.person_id}")
        return created

    def update(self, entity_id: str, entity: Note) -> Optional[Note]:
        with self._sf() as s:
            row = s.get(NoteRow, entity_id)
            if not row:
                return None
            row.content = entity.content
            row.note_type = entity.note_type
            s.commit()
            s.refresh(row)
            return self._to_domain(row)

    def delete(self, entity_id: str) -> bool:
        with self._sf() as s:
            row = s.get(NoteRow, entity_id)
            if not row:
                return False
            s.delete(row)
            s.commit()
        return True

    def delete_by_person(self, person_id: str) -> int:
        with self._sf() as s:
            count = s.query(NoteRow).filter(NoteRow.person_id == person_id).delete()
            s.commit()
        return count

    def count_by_person(self, person_id: str) -> int:
        with self._sf() as s:
            return s.query(NoteRow).filter(NoteRow.person_id == person_id).count()

    def exists(self, filters: dict) -> bool:
        return len(self.find_all(filters)) > 0
