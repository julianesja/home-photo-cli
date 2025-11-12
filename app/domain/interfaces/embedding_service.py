from abc import ABC, abstractmethod
from typing import List, Tuple


class EmbeddingService(ABC):
  @abstractmethod
  def get_embedding(self, file_content: bytes) -> Tuple[bool, List[float] | None, str]:
    pass