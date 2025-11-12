from typing import Optional
from app.domain.repositories.photo_repository import PhotoRepository
from app.infrastructure.repositories.base_repository_orm import BaseRepositoryORM
from app.infrastructure.db.models import Photo as PhotoTable
from app.domain.models.photo import Photo as PhotoModel
from sqlalchemy.orm import Session
import uuid

class PhotoRepositoryORM(BaseRepositoryORM[PhotoModel], PhotoRepository):
    def __init__(self, session: Session):
        super().__init__(PhotoTable, session)

    def get_by_hash(self, hash: str) -> Optional[PhotoModel]:
        result = self._session.query(PhotoTable).filter_by(hash=hash).first()
        if result:
            return PhotoModel(id=result.id, hash=result.hash, path=result.path, path_web=result.path_web)
        return None

    def create_photo(self, obj: PhotoModel) -> PhotoModel:
        photo_table = PhotoTable(
            hash=obj.hash,
            path=obj.path,
            path_web=obj.path_web,
            id=str(uuid.uuid4()),
        )
        self._session.add(photo_table)
        self._session.commit()
        return PhotoModel(id=photo_table.id, hash=photo_table.hash, path=photo_table.path, path_web=photo_table.path_web)