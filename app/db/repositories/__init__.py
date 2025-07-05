"""
Repositorios para el acceso a datos del organizador de fotos.
"""

from .base_repository import BaseRepository
from .photo_repository import PhotoRepository
from .person_repository import PersonRepository
from .face_embedding_repository import FaceEmbeddingRepository
from .photo_people_repository import PhotoPeopleRepository
from .duplicate_repository import DuplicateRepository

__all__ = [
    'BaseRepository',
    'PhotoRepository',
    'PersonRepository',
    'FaceEmbeddingRepository',
    'PhotoPeopleRepository',
    'DuplicateRepository'
] 