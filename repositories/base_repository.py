"""
Base repository with abstract interface
Implements Liskov Substitution Principle - any storage backend can be swapped
"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository
    Defines the interface that all concrete repositories must implement
    """
    
    @abstractmethod
    def find_all(self, filters: Optional[dict] = None) -> List[T]:
        """Find all entities matching optional filters"""
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID"""
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create new entity"""
        pass
    
    @abstractmethod
    def update(self, entity_id: str, entity: T) -> Optional[T]:
        """Update existing entity"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    def exists(self, filters: dict) -> bool:
        """Check if entity exists matching filters"""
        pass

