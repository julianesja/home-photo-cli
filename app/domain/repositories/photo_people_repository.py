from app.domain.repositories.base_repository import BaseRepository
from app.domain.models.photo_people import PhotoPeople
from abc import abstractmethod

class PhotoPeopleRepository(BaseRepository[PhotoPeople]):
    @abstractmethod
    def create_photo_people(self, obj: PhotoPeople) -> PhotoPeople:
        pass

