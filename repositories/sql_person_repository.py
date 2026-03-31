"""
SQLAlchemy-backed PersonRepository.
Same interface as the JSON/MongoDB version — services are unaware of the backend.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from models.person import Person
from models.tables import PersonRow
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class SqlPersonRepository(BaseRepository[Person]):

    def __init__(self, session_factory):
        self._sf = session_factory

    # --- conversions ---

    @staticmethod
    def _to_domain(row: PersonRow) -> Person:
        tags = [t.strip() for t in row.tags_csv.split(",") if t.strip()] if row.tags_csv else []
        return Person(
            id=row.id,
            user_id=row.user_id,
            name=row.name,
            email=row.email or "",
            phone=row.phone or "",
            company=row.company or "",
            job_title=row.job_title or "",
            location=row.location or "",
            linkedin_url=row.linkedin_url or "",
            twitter_handle=row.twitter_handle or "",
            website=row.website or "",
            details=row.details or "",
            how_we_met=row.how_we_met or "",
            profile_image_url=row.profile_image_url or "",
            birthday=row.birthday or "",
            anniversary=row.anniversary or "",
            met_at=row.met_at or "",
            tags=tags,
            next_follow_up=row.next_follow_up or "",
            follow_up_frequency_days=row.follow_up_frequency_days or 0,
            relationship_score=row.relationship_score or 0.0,
            relationship_status=row.relationship_status or "new",
            last_interaction_at=row.last_interaction_at or "",
            interaction_count=row.interaction_count or 0,
            created_at=row.created_at or "",
            updated_at=row.updated_at or "",
        )

    @staticmethod
    def _apply_entity(row: PersonRow, entity: Person):
        """Copy domain fields onto an ORM row."""
        row.user_id = entity.user_id
        row.name = entity.name
        row.email = entity.email
        row.phone = entity.phone
        row.company = entity.company
        row.job_title = entity.job_title
        row.location = entity.location
        row.linkedin_url = entity.linkedin_url
        row.twitter_handle = entity.twitter_handle
        row.website = entity.website
        row.details = entity.details
        row.how_we_met = entity.how_we_met
        row.profile_image_url = entity.profile_image_url
        row.birthday = entity.birthday
        row.anniversary = entity.anniversary
        row.met_at = entity.met_at
        row.tags_csv = ",".join(entity.tags)
        row.next_follow_up = entity.next_follow_up
        row.follow_up_frequency_days = entity.follow_up_frequency_days
        row.relationship_score = entity.relationship_score
        row.relationship_status = entity.relationship_status
        row.last_interaction_at = entity.last_interaction_at
        row.interaction_count = entity.interaction_count
        row.created_at = entity.created_at
        row.updated_at = entity.updated_at

    # --- BaseRepository interface ---

    def find_all(self, filters: Optional[dict] = None) -> List[Person]:
        with self._sf() as s:
            q = s.query(PersonRow)
            if filters:
                for k, v in filters.items():
                    q = q.filter(getattr(PersonRow, k) == v)
            return [self._to_domain(r) for r in q.all()]

    def find_by_id(self, entity_id: str) -> Optional[Person]:
        with self._sf() as s:
            row = s.get(PersonRow, entity_id)
            return self._to_domain(row) if row else None

    def create(self, entity: Person) -> Person:
        if not entity.id:
            entity.id = str(uuid.uuid4())
        row = PersonRow(id=entity.id)
        self._apply_entity(row, entity)
        with self._sf() as s:
            s.add(row)
            s.commit()
            s.refresh(row)
            created = self._to_domain(row)
        logger.info(f"Created person: {created.name} (ID: {created.id})")
        return created

    def update(self, entity_id: str, entity: Person) -> Optional[Person]:
        entity.updated_at = datetime.now().isoformat()
        with self._sf() as s:
            row = s.get(PersonRow, entity_id)
            if not row:
                return None
            self._apply_entity(row, entity)
            s.commit()
            s.refresh(row)
            updated = self._to_domain(row)
        logger.info(f"Updated person: {updated.name} (ID: {entity_id})")
        return updated

    def delete(self, entity_id: str) -> bool:
        with self._sf() as s:
            row = s.get(PersonRow, entity_id)
            if not row:
                return False
            s.delete(row)
            s.commit()
        logger.info(f"Deleted person (ID: {entity_id})")
        return True

    def exists(self, filters: dict) -> bool:
        return len(self.find_all(filters)) > 0

    # --- Extended queries ---

    def search_by_name(self, query: str, user_id: str) -> List[Person]:
        with self._sf() as s:
            rows = (
                s.query(PersonRow)
                .filter(PersonRow.user_id == user_id)
                .filter(PersonRow.name.ilike(f"%{query}%"))
                .all()
            )
            return [self._to_domain(r) for r in rows]

    def search(self, query: str, user_id: str) -> List[Person]:
        """Full-text search across multiple columns."""
        q = f"%{query}%"
        with self._sf() as s:
            rows = (
                s.query(PersonRow)
                .filter(PersonRow.user_id == user_id)
                .filter(
                    PersonRow.name.ilike(q)
                    | PersonRow.company.ilike(q)
                    | PersonRow.job_title.ilike(q)
                    | PersonRow.email.ilike(q)
                    | PersonRow.location.ilike(q)
                    | PersonRow.details.ilike(q)
                    | PersonRow.how_we_met.ilike(q)
                    | PersonRow.tags_csv.ilike(q)
                )
                .all()
            )
            return [self._to_domain(r) for r in rows]

    def find_by_tag(self, tag: str, user_id: str) -> List[Person]:
        people = self.find_all({"user_id": user_id})
        tag_lower = tag.lower()
        return [p for p in people if tag_lower in [t.lower() for t in p.tags]]

    def find_due_followups(self, user_id: str) -> List[Person]:
        today = datetime.now().strftime("%Y-%m-%d")
        with self._sf() as s:
            rows = (
                s.query(PersonRow)
                .filter(PersonRow.user_id == user_id)
                .filter(PersonRow.next_follow_up != "")
                .filter(PersonRow.next_follow_up <= today)
                .all()
            )
            return [self._to_domain(r) for r in rows]

    def get_all_tags(self, user_id: str) -> List[str]:
        people = self.find_all({"user_id": user_id})
        tags = set()
        for p in people:
            tags.update(p.tags)
        return sorted(tags)
