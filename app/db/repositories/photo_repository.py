# db/repositories/photo_repository.py

from app.db.repositories.base_repository import BaseRepository
from app.db.models import Photo
from sqlalchemy.orm import Session

class PhotoRepository(BaseRepository[Photo]):
    def __init__(self, session: Session):
        super().__init__(Photo, session)

    def get_by_hash(self, hash_value: str):
        return self.session.query(self.model).filter_by(hash=hash_value).first()

    def all(self):
        """Devuelve todas las fotos de la base de datos."""
        return self.session.query(self.model).all()

    def get_new_photos(self):
        """Devuelve todas las fotos nuevas (is_new=True)."""
        return self.session.query(self.model).filter(self.model.is_new == True).all()
