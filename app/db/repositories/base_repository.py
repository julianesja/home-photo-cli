# db/base_repository.py

from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Optional

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def get(self, id: int) -> Optional[T]:
        return self.session.get(self.model, id)

    def list_all(self) -> List[T]:
        return self.session.query(self.model).all()

    def create(self, obj_in: dict) -> T:
        obj = self.model(**obj_in)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True
