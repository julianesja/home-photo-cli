from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Optional

from app.domain.repositories.base_repository import BaseRepository

T = TypeVar("T")

class BaseRepositoryORM(BaseRepository[T]):
    def __init__(self, model: Type[T], session: Session):
        self._model:Type[T] = model
        self._session:Session = session

    
    def get_by_id(self, id: str) -> T:
        self._session.get(self._model, id)

    
    def get_all(self) -> List[T]:
        return self._session.query(self._model).all()

    
    def create(self, obj: T) -> T:
        self._session.add(obj)
        self._session.commit()
        self._session.refresh(obj)
        return obj
  
    
    def update(self, obj: T) -> T:
        instance = self._session.get(self._model, obj.id)
        if not instance:
            return None

        for key, value in obj.to_dict().items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.session.commit()
        self.session.refresh(instance)
        return instance
  
    
    def delete(self, id: str) -> bool:
        obj = self._session.get(self._model, id)
        if not obj:
            return False
        self._session.delete(obj)
        self._session.commit()
        return True

    def create_by_list(self, objects: List[T]) -> List[T]:
        self._session.add_all(objects)
        self._session.commit()
        return objects

  