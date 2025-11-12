from abc import abstractmethod
from app.domain.repositories.base_repository import BaseRepository
from app.domain.models.people import People

class PeopleRepository(BaseRepository[People]):
    @abstractmethod
    def get_people_by_id(self, id: str) -> People:
        pass

    @abstractmethod
    def create_people(self, obj: People) -> People:
        pass