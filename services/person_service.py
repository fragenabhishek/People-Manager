"""
Person service
Handles person/contact management business logic
Single Responsibility: Person management operations
"""
from typing import List, Optional

from models.person import Person
from repositories.person_repository import PersonRepository
from utils.validators import Validator, ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)


class PersonService:
    """
    Person service
    Encapsulates all person-related business logic
    """
    
    def __init__(self, person_repository: PersonRepository):
        """
        Initialize person service with dependencies
        
        Args:
            person_repository: Person repository for data access
        """
        self.person_repository = person_repository
    
    def get_all_people(self, user_id: str) -> List[Person]:
        """
        Get all people for a user
        
        Args:
            user_id: User ID to filter by
            
        Returns:
            List of Person entities
        """
        people = self.person_repository.find_all({'user_id': user_id})
        logger.debug(f"Retrieved {len(people)} people for user {user_id}")
        return people
    
    def get_person_by_id(self, person_id: str, user_id: str) -> Optional[Person]:
        """
        Get a specific person by ID
        
        Args:
            person_id: Person ID
            user_id: User ID for authorization
            
        Returns:
            Person entity if found and belongs to user, None otherwise
        """
        person = self.person_repository.find_by_id(person_id)
        
        # Verify ownership
        if person and person.user_id != user_id:
            logger.warning(f"Unauthorized access attempt: user {user_id} tried to access person {person_id}")
            return None
        
        return person
    
    def search_people(self, query: str, user_id: str) -> List[Person]:
        """
        Search people by name
        
        Args:
            query: Search query
            user_id: User ID to filter by
            
        Returns:
            List of matching Person entities
        """
        results = self.person_repository.search_by_name(query, user_id)
        logger.debug(f"Search '{query}' returned {len(results)} results for user {user_id}")
        return results
    
    def create_person(self, name: str, details: str, user_id: str) -> Person:
        """
        Create a new person
        
        Args:
            name: Person's name
            details: Person details
            user_id: User ID (owner)
            
        Returns:
            Created Person entity
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate input
        try:
            Validator.validate_person_data(name, details)
        except ValidationError as e:
            logger.warning(f"Person creation validation failed: {e}")
            raise
        
        # Create person
        person = Person(
            name=name.strip(),
            details=details.strip() if details else "",
            user_id=user_id
        )
        
        created_person = self.person_repository.create(person)
        logger.info(f"Person created: {created_person.name} (ID: {created_person.id})")
        return created_person
    
    def update_person(
        self,
        person_id: str,
        name: Optional[str],
        details: Optional[str],
        user_id: str
    ) -> Optional[Person]:
        """
        Update an existing person
        
        Args:
            person_id: Person ID
            name: New name (optional)
            details: New details (optional)
            user_id: User ID for authorization
            
        Returns:
            Updated Person entity if successful, None if not found/unauthorized
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if person exists and belongs to user
        existing_person = self.get_person_by_id(person_id, user_id)
        if not existing_person:
            logger.warning(f"Update failed: person {person_id} not found or unauthorized")
            return None
        
        # Validate input
        if name is not None:
            try:
                Validator.validate_person_data(name, details)
            except ValidationError as e:
                logger.warning(f"Person update validation failed: {e}")
                raise
        
        # Update person
        if name is not None:
            existing_person.name = name.strip()
        if details is not None:
            existing_person.details = details.strip()
        
        updated_person = self.person_repository.update(person_id, existing_person)
        logger.info(f"Person updated: {updated_person.name} (ID: {person_id})")
        return updated_person
    
    def delete_person(self, person_id: str, user_id: str) -> bool:
        """
        Delete a person
        
        Args:
            person_id: Person ID
            user_id: User ID for authorization
            
        Returns:
            True if deleted successfully, False otherwise
        """
        # Check if person exists and belongs to user
        existing_person = self.get_person_by_id(person_id, user_id)
        if not existing_person:
            logger.warning(f"Delete failed: person {person_id} not found or unauthorized")
            return False
        
        success = self.person_repository.delete(person_id)
        if success:
            logger.info(f"Person deleted (ID: {person_id})")
        return success

