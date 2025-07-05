# db/repositories/photo_repository.py

from app.db.repositories.base_repository import BaseRepository
from app.db.models import Photo
from sqlalchemy.orm import Session

class PhotoRepository(BaseRepository[Photo]):
    def __init__(self, session: Session):
        super().__init__(Photo, session)

    def get_by_hash(self, hash_value: str):
        return self.session.query(self.model).filter_by(hash=hash_value).first()
