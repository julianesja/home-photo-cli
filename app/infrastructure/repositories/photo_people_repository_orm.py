from app.infrastructure.repositories.base_repository_orm import BaseRepositoryORM
from app.domain.repositories.photo_people_repository import PhotoPeopleRepository
from app.domain.models.photo_people import PhotoPeople as PhotoPeopleModel
from app.infrastructure.db.models import PhotoPeople as PhotoPeopleTable
from sqlalchemy.orm import Session

class PhotoPeopleRepositoryORM(BaseRepositoryORM[PhotoPeopleModel], PhotoPeopleRepository):
    def __init__(self, session: Session):
        super().__init__(PhotoPeopleTable, session)

    def create_photo_people(self, obj: PhotoPeopleModel) -> PhotoPeopleModel:
        photo_people_table = PhotoPeopleTable(
            photo_id=obj.photo_id,
            people_id=obj.people_id,
        )
        self._session.add(photo_people_table)
        self._session.commit()
        return PhotoPeopleModel(photo_id=photo_people_table.photo_id, people_id=photo_people_table.people_id)