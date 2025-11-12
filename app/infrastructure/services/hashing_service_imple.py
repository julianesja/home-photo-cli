import hashlib
from app.domain.interfaces.hashing_service import HashingService


class HashingServiceImpl(HashingService):
  def calculate_file_hash(self, file_content: bytes) -> str:
    """Calcula el hash SHA-256 de un archivo."""
    hash_obj = hashlib.sha256(file_content)
    return hash_obj.hexdigest()