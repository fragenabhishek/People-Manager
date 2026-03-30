"""
Import/Export service - handles CSV import and data export
"""
import csv
import io
import json
from typing import List, Tuple
from datetime import datetime

from models.person import Person
from repositories.person_repository import PersonRepository
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)

CSV_FIELD_MAP = {
    'name': 'name',
    'email': 'email',
    'phone': 'phone',
    'company': 'company',
    'job_title': 'job_title',
    'job title': 'job_title',
    'title': 'job_title',
    'location': 'location',
    'city': 'location',
    'linkedin': 'linkedin_url',
    'linkedin_url': 'linkedin_url',
    'twitter': 'twitter_handle',
    'twitter_handle': 'twitter_handle',
    'website': 'website',
    'url': 'website',
    'details': 'details',
    'notes': 'details',
    'how_we_met': 'how_we_met',
    'how we met': 'how_we_met',
    'birthday': 'birthday',
    'tags': 'tags',
    'met_at': 'met_at',
}


class ImportExportService:
    """Handles CSV import and JSON/CSV export"""

    def __init__(self, person_repository: PersonRepository):
        self.person_repository = person_repository

    def import_csv(self, file_content: str, user_id: str) -> Tuple[int, int, List[str]]:
        """
        Import contacts from CSV content.
        Returns (imported_count, skipped_count, errors)
        """
        reader = csv.DictReader(io.StringIO(file_content))
        imported = 0
        skipped = 0
        errors = []

        for row_num, row in enumerate(reader, start=2):
            if row_num > Config.MAX_IMPORT_ROWS + 1:
                errors.append(f"Import limit reached ({Config.MAX_IMPORT_ROWS} rows)")
                break

            mapped = {}
            for csv_col, value in row.items():
                if not csv_col:
                    continue
                key = csv_col.strip().lower()
                field = CSV_FIELD_MAP.get(key)
                if field:
                    mapped[field] = value.strip() if value else ''

            name = mapped.get('name', '').strip()
            if not name:
                skipped += 1
                errors.append(f"Row {row_num}: Missing name, skipped")
                continue

            tags_str = mapped.get('tags', '')
            tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []

            person = Person(
                name=name,
                user_id=user_id,
                email=mapped.get('email', ''),
                phone=mapped.get('phone', ''),
                company=mapped.get('company', ''),
                job_title=mapped.get('job_title', ''),
                location=mapped.get('location', ''),
                linkedin_url=mapped.get('linkedin_url', ''),
                twitter_handle=mapped.get('twitter_handle', ''),
                website=mapped.get('website', ''),
                details=mapped.get('details', ''),
                how_we_met=mapped.get('how_we_met', ''),
                birthday=mapped.get('birthday', ''),
                met_at=mapped.get('met_at', ''),
                tags=tags,
            )

            try:
                self.person_repository.create(person)
                imported += 1
            except Exception as e:
                skipped += 1
                errors.append(f"Row {row_num}: {str(e)}")

        logger.info(f"CSV import: {imported} imported, {skipped} skipped for user {user_id}")
        return imported, skipped, errors

    def export_csv(self, user_id: str) -> str:
        """Export all contacts as CSV string"""
        people = self.person_repository.find_all({'user_id': user_id})
        output = io.StringIO()
        fieldnames = [
            'name', 'email', 'phone', 'company', 'job_title', 'location',
            'linkedin_url', 'twitter_handle', 'website', 'details',
            'how_we_met', 'birthday', 'anniversary', 'met_at', 'tags',
            'next_follow_up', 'created_at', 'updated_at',
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for person in people:
            writer.writerow({
                'name': person.name,
                'email': person.email,
                'phone': person.phone,
                'company': person.company,
                'job_title': person.job_title,
                'location': person.location,
                'linkedin_url': person.linkedin_url,
                'twitter_handle': person.twitter_handle,
                'website': person.website,
                'details': person.details,
                'how_we_met': person.how_we_met,
                'birthday': person.birthday,
                'anniversary': person.anniversary,
                'met_at': person.met_at,
                'tags': ', '.join(person.tags),
                'next_follow_up': person.next_follow_up,
                'created_at': person.created_at,
                'updated_at': person.updated_at,
            })

        return output.getvalue()

    def export_json(self, user_id: str) -> str:
        """Export all contacts as JSON string"""
        people = self.person_repository.find_all({'user_id': user_id})
        data = [p.to_dict() for p in people]
        for d in data:
            d.pop('user_id', None)
        return json.dumps(data, indent=2)
