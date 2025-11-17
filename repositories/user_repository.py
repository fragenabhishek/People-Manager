"""
User repository with dual storage support (MongoDB/JSON)
"""
import json
import os
from typing import List, Optional
from datetime import datetime

from models.user import User
from repositories.base_repository import BaseRepository
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """User repository supporting both MongoDB and JSON storage"""
    
    def __init__(self, users_collection=None, data_file: str = None):
        """
        Initialize repository with optional MongoDB collection or file path
        
        Args:
            users_collection: MongoDB collection (if using MongoDB)
            data_file: JSON file path (if using file storage)
        """
        self.use_mongodb = Config.USE_MONGODB
        self.users_collection = users_collection
        self.data_file = data_file or Config.USERS_FILE
        
        # Initialize file storage if needed
        if not self.use_mongodb and not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)
    
    def find_all(self, filters: Optional[dict] = None) -> List[User]:
        """Find all users matching optional filters"""
        if self.use_mongodb:
            return self._find_all_mongodb(filters)
        return self._find_all_json(filters)
    
    def _find_all_mongodb(self, filters: Optional[dict]) -> List[User]:
        """MongoDB implementation"""
        try:
            query = filters or {}
            users_data = list(self.users_collection.find(query))
            users = []
            
            for data in users_data:
                data['_id'] = str(data['_id'])
                if 'id' not in data:
                    data['id'] = data['_id']
                users.append(User.from_dict(data))
            
            return users
        except Exception as e:
            logger.error(f"Error finding users in MongoDB: {e}")
            raise
    
    def _find_all_json(self, filters: Optional[dict]) -> List[User]:
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
            
            return [User.from_dict(data) for data in filtered_data]
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Error reading users from file: {e}")
            raise
    
    def find_by_id(self, entity_id: str) -> Optional[User]:
        """Find user by ID"""
        if self.use_mongodb:
            return self._find_by_id_mongodb(entity_id)
        return self._find_by_id_json(entity_id)
    
    def _find_by_id_mongodb(self, entity_id: str) -> Optional[User]:
        """MongoDB implementation"""
        try:
            data = self.users_collection.find_one({'id': entity_id})
            if data:
                data['_id'] = str(data['_id'])
                return User.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Error finding user by ID in MongoDB: {e}")
            raise
    
    def _find_by_id_json(self, entity_id: str) -> Optional[User]:
        """JSON file implementation"""
        users = self.find_all()
        return next((u for u in users if u.id == entity_id), None)
    
    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        if self.use_mongodb:
            try:
                data = self.users_collection.find_one({'username': username})
                if data:
                    data['_id'] = str(data['_id'])
                    if 'id' not in data:
                        data['id'] = data['_id']
                    return User.from_dict(data)
                return None
            except Exception as e:
                logger.error(f"Error finding user by username in MongoDB: {e}")
                raise
        else:
            users = self.find_all()
            return next((u for u in users if u.username == username), None)
    
    def create(self, entity: User) -> User:
        """Create new user"""
        # Generate ID if not present
        if not entity.id:
            entity.id = str(int(datetime.now().timestamp() * 1000))
        
        if self.use_mongodb:
            return self._create_mongodb(entity)
        return self._create_json(entity)
    
    def _create_mongodb(self, entity: User) -> User:
        """MongoDB implementation"""
        try:
            result = self.users_collection.insert_one(entity.to_dict())
            entity.id = entity.id or str(result.inserted_id)
            logger.info(f"Created user: {entity.username} (ID: {entity.id})")
            return entity
        except Exception as e:
            logger.error(f"Error creating user in MongoDB: {e}")
            raise
    
    def _create_json(self, entity: User) -> User:
        """JSON file implementation"""
        try:
            users = self.find_all()
            users.append(entity)
            self._write_json([u.to_dict() for u in users])
            logger.info(f"Created user: {entity.username} (ID: {entity.id})")
            return entity
        except Exception as e:
            logger.error(f"Error creating user in file: {e}")
            raise
    
    def update(self, entity_id: str, entity: User) -> Optional[User]:
        """Update existing user"""
        if self.use_mongodb:
            return self._update_mongodb(entity_id, entity)
        return self._update_json(entity_id, entity)
    
    def _update_mongodb(self, entity_id: str, entity: User) -> Optional[User]:
        """MongoDB implementation"""
        try:
            update_data = entity.to_dict()
            result = self.users_collection.find_one_and_update(
                {'id': entity_id},
                {'$set': update_data},
                return_document=True
            )
            
            if result:
                result['_id'] = str(result['_id'])
                logger.info(f"Updated user: {entity.username} (ID: {entity_id})")
                return User.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Error updating user in MongoDB: {e}")
            raise
    
    def _update_json(self, entity_id: str, entity: User) -> Optional[User]:
        """JSON file implementation"""
        try:
            users = self.find_all()
            user_index = next((i for i, u in enumerate(users) if u.id == entity_id), None)
            
            if user_index is None:
                return None
            
            entity.id = entity_id  # Ensure ID is preserved
            users[user_index] = entity
            self._write_json([u.to_dict() for u in users])
            logger.info(f"Updated user: {entity.username} (ID: {entity_id})")
            return entity
        except Exception as e:
            logger.error(f"Error updating user in file: {e}")
            raise
    
    def delete(self, entity_id: str) -> bool:
        """Delete user by ID"""
        if self.use_mongodb:
            return self._delete_mongodb(entity_id)
        return self._delete_json(entity_id)
    
    def _delete_mongodb(self, entity_id: str) -> bool:
        """MongoDB implementation"""
        try:
            result = self.users_collection.delete_one({'id': entity_id})
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted user (ID: {entity_id})")
            return success
        except Exception as e:
            logger.error(f"Error deleting user from MongoDB: {e}")
            raise
    
    def _delete_json(self, entity_id: str) -> bool:
        """JSON file implementation"""
        try:
            users = self.find_all()
            original_length = len(users)
            users = [u for u in users if u.id != entity_id]
            
            if len(users) == original_length:
                return False
            
            self._write_json([u.to_dict() for u in users])
            logger.info(f"Deleted user (ID: {entity_id})")
            return True
        except Exception as e:
            logger.error(f"Error deleting user from file: {e}")
            raise
    
    def exists(self, filters: dict) -> bool:
        """Check if user exists matching filters"""
        users = self.find_all(filters)
        return len(users) > 0
    
    def _write_json(self, data: list) -> None:
        """Write data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

