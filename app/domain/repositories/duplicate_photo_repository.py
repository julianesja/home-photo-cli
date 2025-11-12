from abc import abstractmethod
from typing import List
from app.domain.repositories.base_repository import BaseRepository
from app.domain.models.duplicate_photo import DuplicatePhoto

class DuplicatePhotoRepository(BaseRepository[DuplicatePhoto]):
	@abstractmethod
	def save_duplicate_photo(self, id: str, duplicate_of_ids: List[str]) -> List[DuplicatePhoto]:
		pass