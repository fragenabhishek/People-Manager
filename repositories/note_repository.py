"""
Note repository with dual storage support (MongoDB/JSON)
"""
import json
import os
from typing import List, Optional
from datetime import datetime

from models.note import Note
from repositories.base_repository import BaseRepository
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class NoteRepository(BaseRepository[Note]):
    """Note repository supporting both MongoDB and JSON storage"""

    def __init__(self, notes_collection=None, data_file: str = None):
        self.use_mongodb = Config.USE_MONGODB
        self.notes_collection = notes_collection
        self.data_file = data_file or Config.NOTES_FILE

        if not self.use_mongodb and not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)

    def find_all(self, filters: Optional[dict] = None) -> List[Note]:
        if self.use_mongodb:
            return self._find_all_mongodb(filters)
        return self._find_all_json(filters)

    def _find_all_mongodb(self, filters: Optional[dict]) -> List[Note]:
        try:
            query = filters or {}
            data_list = list(self.notes_collection.find(query).sort('created_at', -1))
            notes = []
            for data in data_list:
                data['_id'] = str(data['_id'])
                if 'id' not in data:
                    data['id'] = data['_id']
                notes.append(Note.from_dict(data))
            return notes
        except Exception as e:
            logger.error(f"Error finding notes in MongoDB: {e}")
            raise

    def _find_all_json(self, filters: Optional[dict]) -> List[Note]:
        try:
            with open(self.data_file, 'r') as f:
                all_data = json.load(f)
            if filters:
                filtered = [
                    item for item in all_data
                    if all(item.get(k) == v for k, v in filters.items())
                ]
            else:
                filtered = all_data
            notes = [Note.from_dict(d) for d in filtered]
            notes.sort(key=lambda n: n.created_at, reverse=True)
            return notes
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Error reading notes from file: {e}")
            raise

    def find_by_id(self, entity_id: str) -> Optional[Note]:
        if self.use_mongodb:
            try:
                data = self.notes_collection.find_one({'id': entity_id})
                if data:
                    data['_id'] = str(data['_id'])
                    return Note.from_dict(data)
                return None
            except Exception as e:
                logger.error(f"Error finding note by ID: {e}")
                raise
        else:
            notes = self.find_all()
            return next((n for n in notes if n.id == entity_id), None)

    def find_by_person(self, person_id: str, user_id: str) -> List[Note]:
        return self.find_all({'person_id': person_id, 'user_id': user_id})

    def create(self, entity: Note) -> Note:
        if not entity.id:
            entity.id = str(int(datetime.now().timestamp() * 1000))
        if self.use_mongodb:
            try:
                self.notes_collection.insert_one(entity.to_dict())
                logger.info(f"Created note (ID: {entity.id}) for person {entity.person_id}")
                return entity
            except Exception as e:
                logger.error(f"Error creating note in MongoDB: {e}")
                raise
        else:
            try:
                notes = self.find_all()
                notes.append(entity)
                self._write_json([n.to_dict() for n in notes])
                logger.info(f"Created note (ID: {entity.id}) for person {entity.person_id}")
                return entity
            except Exception as e:
                logger.error(f"Error creating note in file: {e}")
                raise

    def update(self, entity_id: str, entity: Note) -> Optional[Note]:
        if self.use_mongodb:
            try:
                result = self.notes_collection.find_one_and_update(
                    {'id': entity_id},
                    {'$set': entity.to_dict()},
                    return_document=True
                )
                if result:
                    result['_id'] = str(result['_id'])
                    return Note.from_dict(result)
                return None
            except Exception as e:
                logger.error(f"Error updating note: {e}")
                raise
        else:
            try:
                notes = self.find_all()
                idx = next((i for i, n in enumerate(notes) if n.id == entity_id), None)
                if idx is None:
                    return None
                entity.id = entity_id
                notes[idx] = entity
                self._write_json([n.to_dict() for n in notes])
                return entity
            except Exception as e:
                logger.error(f"Error updating note in file: {e}")
                raise

    def delete(self, entity_id: str) -> bool:
        if self.use_mongodb:
            try:
                result = self.notes_collection.delete_one({'id': entity_id})
                return result.deleted_count > 0
            except Exception as e:
                logger.error(f"Error deleting note from MongoDB: {e}")
                raise
        else:
            try:
                notes = self.find_all()
                original = len(notes)
                notes = [n for n in notes if n.id != entity_id]
                if len(notes) == original:
                    return False
                self._write_json([n.to_dict() for n in notes])
                return True
            except Exception as e:
                logger.error(f"Error deleting note from file: {e}")
                raise

    def delete_by_person(self, person_id: str) -> int:
        """Delete all notes for a person. Returns count deleted."""
        if self.use_mongodb:
            try:
                result = self.notes_collection.delete_many({'person_id': person_id})
                return result.deleted_count
            except Exception as e:
                logger.error(f"Error bulk-deleting notes: {e}")
                raise
        else:
            try:
                notes = self.find_all()
                original = len(notes)
                notes = [n for n in notes if n.person_id != person_id]
                self._write_json([n.to_dict() for n in notes])
                return original - len(notes)
            except Exception as e:
                logger.error(f"Error bulk-deleting notes from file: {e}")
                raise

    def count_by_person(self, person_id: str) -> int:
        return len(self.find_all({'person_id': person_id}))

    def exists(self, filters: dict) -> bool:
        return len(self.find_all(filters)) > 0

    def _write_json(self, data: list) -> None:
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
