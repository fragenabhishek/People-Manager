"""
SQLAlchemy-backed UserRepository.
Same interface as the JSON/MongoDB version — services are unaware of the backend.
"""
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from models.tables import UserRow
from models.user import User
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class SqlUserRepository(BaseRepository[User]):

    def __init__(self, session_factory):
        self._sf = session_factory

    # --- conversions ---

    @staticmethod
    def _to_domain(row: UserRow) -> User:
        return User(
            id=row.id,
            username=row.username,
            password_hash=row.password_hash,
            email=row.email,
            mfa_secret=row.mfa_secret,
            mfa_enabled=row.mfa_enabled,
            is_active=row.is_active,
            created_at=row.created_at.isoformat() if hasattr(row.created_at, 'isoformat') else str(row.created_at),
        )

    @staticmethod
    def _to_row(entity: User) -> UserRow:
        return UserRow(
            id=entity.id or str(uuid.uuid4()),
            username=entity.username,
            password_hash=entity.password_hash,
            email=entity.email or None,
            mfa_secret=entity.mfa_secret,
            mfa_enabled=entity.mfa_enabled,
            is_active=entity.is_active,
        )

    # --- BaseRepository interface ---

    def find_all(self, filters: Optional[dict] = None) -> List[User]:
        with self._sf() as s:
            q = s.query(UserRow)
            if filters:
                for k, v in filters.items():
                    q = q.filter(getattr(UserRow, k) == v)
            return [self._to_domain(r) for r in q.all()]

    def find_by_id(self, entity_id: str) -> Optional[User]:
        with self._sf() as s:
            row = s.get(UserRow, entity_id)
            return self._to_domain(row) if row else None

    def find_by_username(self, username: str) -> Optional[User]:
        with self._sf() as s:
            row = s.query(UserRow).filter(UserRow.username == username).first()
            return self._to_domain(row) if row else None

    def create(self, entity: User) -> User:
        if not entity.id:
            entity.id = str(uuid.uuid4())
        row = self._to_row(entity)
        with self._sf() as s:
            s.add(row)
            s.commit()
            s.refresh(row)
            created = self._to_domain(row)
        logger.info(f"Created user: {created.username} (ID: {created.id})")
        return created

    def update(self, entity_id: str, entity: User) -> Optional[User]:
        with self._sf() as s:
            row = s.get(UserRow, entity_id)
            if not row:
                return None
            row.username = entity.username
            row.password_hash = entity.password_hash
            row.email = entity.email or None
            row.mfa_secret = entity.mfa_secret
            row.mfa_enabled = entity.mfa_enabled
            row.is_active = entity.is_active
            s.commit()
            s.refresh(row)
            updated = self._to_domain(row)
        logger.info(f"Updated user: {updated.username} (ID: {entity_id})")
        return updated

    def delete(self, entity_id: str) -> bool:
        with self._sf() as s:
            row = s.get(UserRow, entity_id)
            if not row:
                return False
            s.delete(row)
            s.commit()
        logger.info(f"Deleted user (ID: {entity_id})")
        return True

    def exists(self, filters: dict) -> bool:
        return len(self.find_all(filters)) > 0
