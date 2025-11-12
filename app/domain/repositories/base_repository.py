from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic 

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def get_by_id(self, id: str) -> T:
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        pass

    @abstractmethod
    def create(self, obj: T) -> T:
        pass

    @abstractmethod
    def create_by_list(self, objects: List[T]) -> List[T]:
        pass
  
    @abstractmethod
    def update(self, obj: T) -> T:
        pass
  
    @abstractmethod
    def delete(self, id: str) -> bool:
        pass