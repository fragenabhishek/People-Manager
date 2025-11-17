"""
Person repository with dual storage support (MongoDB/JSON)
Implements Repository Pattern for data access abstraction
"""
import json
import os
from typing import List, Optional
from datetime import datetime

from models.person import Person
from repositories.base_repository import BaseRepository
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class PersonRepository(BaseRepository[Person]):
    """
    Person repository supporting both MongoDB and JSON storage
    Implements Dependency Inversion: depends on abstraction, not concrete implementation
    """
    
    def __init__(self, people_collection=None, data_file: str = None):
        """
        Initialize repository with optional MongoDB collection or file path
        
        Args:
            people_collection: MongoDB collection (if using MongoDB)
            data_file: JSON file path (if using file storage)
        """
        self.use_mongodb = Config.USE_MONGODB
        self.people_collection = people_collection
        self.data_file = data_file or Config.DATA_FILE
        
        # Initialize file storage if needed
        if not self.use_mongodb and not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)
    
    def find_all(self, filters: Optional[dict] = None) -> List[Person]:
        """
        Find all people matching optional filters
        
        Args:
            filters: Optional filter criteria (e.g., {'user_id': '123'})
            
        Returns:
            List of Person entities
        """
        if self.use_mongodb:
            return self._find_all_mongodb(filters)
        return self._find_all_json(filters)
    
    def _find_all_mongodb(self, filters: Optional[dict]) -> List[Person]:
        """MongoDB implementation"""
        try:
            query = filters or {}
            people_data = list(self.people_collection.find(query))
            people = []
            
            for data in people_data:
                data['_id'] = str(data['_id'])
                if 'id' not in data:
                    data['id'] = data['_id']
                people.append(Person.from_dict(data))
            
            return people
        except Exception as e:
            logger.error(f"Error finding people in MongoDB: {e}")
            raise
    
    def _find_all_json(self, filters: Optional[dict]) -> List[Person]:
        """JSON file implementation"""
        try:
            with open(self.data_file, 'r') as f:
                all_data = json.load(f)
            
            # Apply filters
            if filters:
                filtered_data = [
                    item for item in all_data
                    if all(item.get(key) == value for key, value in filters.items())
                ]
            else:
                filtered_data = all_data
            
            return [Person.from_dict(data) for data in filtered_data]
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Error reading people from file: {e}")
            raise
    
    def find_by_id(self, entity_id: str) -> Optional[Person]:
        """Find person by ID"""
        if self.use_mongodb:
            return self._find_by_id_mongodb(entity_id)
        return self._find_by_id_json(entity_id)
    
    def _find_by_id_mongodb(self, entity_id: str) -> Optional[Person]:
        """MongoDB implementation"""
        try:
            data = self.people_collection.find_one({'id': entity_id})
            if data:
                data['_id'] = str(data['_id'])
                return Person.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Error finding person by ID in MongoDB: {e}")
            raise
    
    def _find_by_id_json(self, entity_id: str) -> Optional[Person]:
        """JSON file implementation"""
        people = self.find_all()
        return next((p for p in people if p.id == entity_id), None)
    
    def create(self, entity: Person) -> Person:
        """Create new person"""
        # Generate ID if not present
        if not entity.id:
            entity.id = str(int(datetime.now().timestamp() * 1000))
        
        if self.use_mongodb:
            return self._create_mongodb(entity)
        return self._create_json(entity)
    
    def _create_mongodb(self, entity: Person) -> Person:
        """MongoDB implementation"""
        try:
            result = self.people_collection.insert_one(entity.to_dict())
            entity.id = entity.id or str(result.inserted_id)
            logger.info(f"Created person: {entity.name} (ID: {entity.id})")
            return entity
        except Exception as e:
            logger.error(f"Error creating person in MongoDB: {e}")
            raise
    
    def _create_json(self, entity: Person) -> Person:
        """JSON file implementation"""
        try:
            people = self.find_all()
            people.append(entity)
            self._write_json([p.to_dict() for p in people])
            logger.info(f"Created person: {entity.name} (ID: {entity.id})")
            return entity
        except Exception as e:
            logger.error(f"Error creating person in file: {e}")
            raise
    
    def update(self, entity_id: str, entity: Person) -> Optional[Person]:
        """Update existing person"""
        entity.updated_at = datetime.now().isoformat()
        
        if self.use_mongodb:
            return self._update_mongodb(entity_id, entity)
        return self._update_json(entity_id, entity)
    
    def _update_mongodb(self, entity_id: str, entity: Person) -> Optional[Person]:
        """MongoDB implementation"""
        try:
            update_data = entity.to_dict()
            result = self.people_collection.find_one_and_update(
                {'id': entity_id},
                {'$set': update_data},
                return_document=True
            )
            
            if result:
                result['_id'] = str(result['_id'])
                logger.info(f"Updated person: {entity.name} (ID: {entity_id})")
                return Person.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Error updating person in MongoDB: {e}")
            raise
    
    def _update_json(self, entity_id: str, entity: Person) -> Optional[Person]:
        """JSON file implementation"""
        try:
            people = self.find_all()
            person_index = next((i for i, p in enumerate(people) if p.id == entity_id), None)
            
            if person_index is None:
                return None
            
            entity.id = entity_id  # Ensure ID is preserved
            people[person_index] = entity
            self._write_json([p.to_dict() for p in people])
            logger.info(f"Updated person: {entity.name} (ID: {entity_id})")
            return entity
        except Exception as e:
            logger.error(f"Error updating person in file: {e}")
            raise
    
    def delete(self, entity_id: str) -> bool:
        """Delete person by ID"""
        if self.use_mongodb:
            return self._delete_mongodb(entity_id)
        return self._delete_json(entity_id)
    
    def _delete_mongodb(self, entity_id: str) -> bool:
        """MongoDB implementation"""
        try:
            result = self.people_collection.delete_one({'id': entity_id})
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted person (ID: {entity_id})")
            return success
        except Exception as e:
            logger.error(f"Error deleting person from MongoDB: {e}")
            raise
    
    def _delete_json(self, entity_id: str) -> bool:
        """JSON file implementation"""
        try:
            people = self.find_all()
            original_length = len(people)
            people = [p for p in people if p.id != entity_id]
            
            if len(people) == original_length:
                return False
            
            self._write_json([p.to_dict() for p in people])
            logger.info(f"Deleted person (ID: {entity_id})")
            return True
        except Exception as e:
            logger.error(f"Error deleting person from file: {e}")
            raise
    
    def exists(self, filters: dict) -> bool:
        """Check if person exists matching filters"""
        people = self.find_all(filters)
        return len(people) > 0
    
    def search_by_name(self, query: str, user_id: str) -> List[Person]:
        """
        Search people by name
        
        Args:
            query: Search query
            user_id: User ID to filter by
            
        Returns:
            List of matching Person entities
        """
        people = self.find_all({'user_id': user_id})
        query_lower = query.lower()
        return [p for p in people if query_lower in p.name.lower()]
    
    def _write_json(self, data: list) -> None:
        """Write data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

