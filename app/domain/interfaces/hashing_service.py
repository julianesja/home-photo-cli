from abc import ABC, abstractmethod


class HashingService(ABC):
  @abstractmethod
  def calculate_file_hash(self, file_content: bytes) -> str:
    pass