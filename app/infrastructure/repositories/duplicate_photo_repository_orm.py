from typing import List
from app.infrastructure.repositories.base_repository_orm import BaseRepositoryORM
from app.domain.models.duplicate_photo import DuplicatePhoto as DuplicatePhotoModel
from app.domain.repositories.duplicate_photo_repository import DuplicatePhotoRepository
from app.infrastructure.db.models import Duplicate as DuplicateTable
from sqlalchemy.orm import Session


class DuplicatePhotoRepositoryORM(BaseRepositoryORM[DuplicatePhotoModel], DuplicatePhotoRepository):
    def __init__(self, session: Session):
        super().__init__(DuplicateTable, session)
    
    def save_duplicate_photo(self, id: str, duplicate_of_ids: List[str]) -> List[DuplicatePhotoModel]:
        duplicate_tables = [
            DuplicateTable(
                photo_id=id,
                duplicate_of_id=duplicate_of_id,
            )
            for duplicate_of_id in duplicate_of_ids
        ]
        self.create_by_list(duplicate_tables)