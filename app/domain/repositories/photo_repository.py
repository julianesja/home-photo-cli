from typing import Optional
from app.domain.models.photo import Photo
from app.domain.repositories.base_repository import BaseRepository
from abc import abstractmethod

class PhotoRepository(BaseRepository[Photo]):
    @abstractmethod
    def get_by_hash(self, hash: str) -> Optional[Photo]:
        pass

    @abstractmethod
    def create_photo(self, obj: Photo) -> Photo:
        pass
        