"""
Person service - handles contact management business logic
"""
from typing import List, Optional
from datetime import datetime, timedelta

from models.person import Person
from repositories.person_repository import PersonRepository
from repositories.note_repository import NoteRepository
from utils.validators import Validator, ValidationError
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)


class PersonService:
    """Encapsulates all person-related business logic"""

    def __init__(self, person_repository: PersonRepository, note_repository: NoteRepository = None):
        self.person_repository = person_repository
        self.note_repository = note_repository

    def get_all_people(self, user_id: str) -> List[Person]:
        people = self.person_repository.find_all({'user_id': user_id})
        if self.note_repository:
            for person in people:
                old_score = person.relationship_score
                old_status = person.relationship_status
                self._refresh_relationship_score(person)
                if person.relationship_score != old_score or person.relationship_status != old_status:
                    self.person_repository.update(person.id, person)
        logger.debug(f"Retrieved {len(people)} people for user {user_id}")
        return people

    def get_person_by_id(self, person_id: str, user_id: str) -> Optional[Person]:
        person = self.person_repository.find_by_id(person_id)
        if person and person.user_id != user_id:
            logger.warning(f"Unauthorized access attempt: user {user_id} -> person {person_id}")
            return None
        return person

    def search_people(self, query: str, user_id: str) -> List[Person]:
        results = self.person_repository.search(query, user_id)
        logger.debug(f"Search '{query}' returned {len(results)} results for user {user_id}")
        return results

    def create_person(self, user_id: str, **kwargs) -> Person:
        """Create a new person with structured fields"""
        name = kwargs.get('name', '').strip()
        try:
            Validator.validate_person_data(name, kwargs.get('details'))
        except ValidationError:
            raise

        tags = kwargs.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]

        person = Person(
            name=name,
            user_id=user_id,
            email=kwargs.get('email', '').strip(),
            phone=kwargs.get('phone', '').strip(),
            company=kwargs.get('company', '').strip(),
            job_title=kwargs.get('job_title', '').strip(),
            location=kwargs.get('location', '').strip(),
            linkedin_url=kwargs.get('linkedin_url', '').strip(),
            twitter_handle=kwargs.get('twitter_handle', '').strip(),
            website=kwargs.get('website', '').strip(),
            details=kwargs.get('details', '').strip(),
            how_we_met=kwargs.get('how_we_met', '').strip(),
            profile_image_url=kwargs.get('profile_image_url', '').strip(),
            birthday=kwargs.get('birthday', ''),
            anniversary=kwargs.get('anniversary', ''),
            met_at=kwargs.get('met_at', ''),
            tags=tags,
            next_follow_up=kwargs.get('next_follow_up', ''),
            follow_up_frequency_days=int(kwargs.get('follow_up_frequency_days', 0) or 0),
            relationship_status='new',
        )

        created = self.person_repository.create(person)
        logger.info(f"Person created: {created.name} (ID: {created.id})")
        return created

    def update_person(self, person_id: str, user_id: str, **kwargs) -> Optional[Person]:
        existing = self.get_person_by_id(person_id, user_id)
        if not existing:
            return None

        name = kwargs.get('name')
        if name is not None:
            try:
                Validator.validate_person_data(name, kwargs.get('details'))
            except ValidationError:
                raise

        tags = kwargs.get('tags')
        if tags is not None and isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]
            kwargs['tags'] = tags

        updatable_fields = [
            'name', 'email', 'phone', 'company', 'job_title', 'location',
            'linkedin_url', 'twitter_handle', 'website', 'details',
            'how_we_met', 'profile_image_url', 'birthday', 'anniversary',
            'met_at', 'tags', 'next_follow_up', 'follow_up_frequency_days',
        ]
        for field in updatable_fields:
            value = kwargs.get(field)
            if value is not None:
                if isinstance(value, str):
                    value = value.strip()
                setattr(existing, field, value)

        updated = self.person_repository.update(person_id, existing)
        if updated:
            logger.info(f"Person updated: {updated.name} (ID: {person_id})")
        return updated

    def delete_person(self, person_id: str, user_id: str) -> bool:
        existing = self.get_person_by_id(person_id, user_id)
        if not existing:
            return False
        success = self.person_repository.delete(person_id)
        if success and self.note_repository:
            self.note_repository.delete_by_person(person_id)
            logger.info(f"Person and notes deleted (ID: {person_id})")
        return success

    # --- Tags ---

    def add_tags(self, person_id: str, user_id: str, tags: List[str]) -> Optional[Person]:
        person = self.get_person_by_id(person_id, user_id)
        if not person:
            return None
        existing_lower = {t.lower() for t in person.tags}
        for tag in tags:
            tag = tag.strip()
            if tag and tag.lower() not in existing_lower:
                person.tags.append(tag)
                existing_lower.add(tag.lower())
        return self.person_repository.update(person_id, person)

    def remove_tag(self, person_id: str, user_id: str, tag: str) -> Optional[Person]:
        person = self.get_person_by_id(person_id, user_id)
        if not person:
            return None
        tag_lower = tag.lower()
        person.tags = [t for t in person.tags if t.lower() != tag_lower]
        return self.person_repository.update(person_id, person)

    def get_all_tags(self, user_id: str) -> List[str]:
        return self.person_repository.get_all_tags(user_id)

    def get_by_tag(self, tag: str, user_id: str) -> List[Person]:
        return self.person_repository.find_by_tag(tag, user_id)

    # --- Follow-ups ---

    def get_due_followups(self, user_id: str) -> List[Person]:
        return self.person_repository.find_due_followups(user_id)

    def set_follow_up(self, person_id: str, user_id: str, date: str, frequency_days: int = 0) -> Optional[Person]:
        person = self.get_person_by_id(person_id, user_id)
        if not person:
            return None
        person.next_follow_up = date
        person.follow_up_frequency_days = frequency_days
        return self.person_repository.update(person_id, person)

    def complete_follow_up(self, person_id: str, user_id: str) -> Optional[Person]:
        """Mark follow-up done; auto-schedule next if recurring"""
        person = self.get_person_by_id(person_id, user_id)
        if not person:
            return None
        if person.follow_up_frequency_days > 0:
            next_date = datetime.now() + timedelta(days=person.follow_up_frequency_days)
            person.next_follow_up = next_date.strftime('%Y-%m-%d')
        else:
            person.next_follow_up = ''
        return self.person_repository.update(person_id, person)

    # --- Relationship scoring ---

    def _refresh_relationship_score(self, person: Person) -> None:
        """Recalculate relationship score in-place based on interaction history"""
        if not self.note_repository:
            return

        notes = self.note_repository.find_by_person(person.id, person.user_id)
        person.interaction_count = len(notes)

        if not notes:
            person.relationship_score = 0.0
            person.relationship_status = 'new' if not person.details else 'cold'
            return

        latest = max(notes, key=lambda n: n.created_at)
        person.last_interaction_at = latest.created_at

        try:
            last_dt = datetime.fromisoformat(latest.created_at)
            days_since = (datetime.now() - last_dt).days
        except (ValueError, TypeError):
            days_since = 999

        recency_score = max(0, 100 - (days_since * 2))
        frequency_score = min(100, person.interaction_count * 10)
        person.relationship_score = round((recency_score * 0.6 + frequency_score * 0.4), 1)

        if days_since <= Config.RELATIONSHIP_WARM_DAYS:
            person.relationship_status = 'warm'
        elif days_since <= Config.RELATIONSHIP_LUKEWARM_DAYS:
            person.relationship_status = 'lukewarm'
        else:
            person.relationship_status = 'cold'

    # --- Dashboard stats ---

    def get_dashboard_stats(self, user_id: str) -> dict:
        people = self.get_all_people(user_id)
        now = datetime.now()
        week_ago = (now - timedelta(days=7)).isoformat()
        month_ago = (now - timedelta(days=30)).isoformat()

        added_this_week = sum(1 for p in people if p.created_at >= week_ago)
        added_this_month = sum(1 for p in people if p.created_at >= month_ago)
        due_followups = [p for p in people if p.next_follow_up and p.next_follow_up <= now.strftime('%Y-%m-%d')]
        cold_contacts = [p for p in people if p.relationship_status == 'cold']

        tag_counts = {}
        for p in people:
            for tag in p.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        status_counts = {'warm': 0, 'lukewarm': 0, 'cold': 0, 'new': 0}
        for p in people:
            status_counts[p.relationship_status] = status_counts.get(p.relationship_status, 0) + 1

        return {
            'total_contacts': len(people),
            'added_this_week': added_this_week,
            'added_this_month': added_this_month,
            'due_followups': len(due_followups),
            'due_followup_list': [p.to_dict() for p in due_followups[:5]],
            'cold_contacts': len(cold_contacts),
            'cold_contact_list': [p.to_dict() for p in cold_contacts[:5]],
            'recently_added': [p.to_dict() for p in sorted(people, key=lambda x: x.created_at, reverse=True)[:5]],
            'tag_counts': tag_counts,
            'status_counts': status_counts,
        }
