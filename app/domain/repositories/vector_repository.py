from abc import ABC, abstractmethod
from typing import List, Tuple


class VectorRepository(ABC):

    @abstractmethod
    def add_vector(self, vector: List[float],id: str):
        pass

    @abstractmethod
    def search_ids(self, vector: List[float])-> Tuple[bool, List[str] | None, str]:
        pass

    @abstractmethod
    def delete_by_id(self, id: str):
        pass