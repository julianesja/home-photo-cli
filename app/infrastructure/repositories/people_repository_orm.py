from app.domain.repositories.people_repository import PeopleRepository
from app.infrastructure.repositories.base_repository_orm import BaseRepositoryORM
from app.infrastructure.db.models import People as PeopleTable
from app.domain.models.people import People as PeopleModel
from sqlalchemy.orm import Session
import uuid

class PeopleRepositoryORM(BaseRepositoryORM[PeopleModel], PeopleRepository):
	def __init__(self, session: Session):
		super().__init__(PeopleTable, session)

	def get_people_by_id(self, id: str) -> PeopleModel:
		return self._session.query(PeopleTable).filter_by(id=id).first()
	
	def create_people(self, obj: PeopleModel) -> PeopleModel:
		people_table = PeopleTable(
			id=str(uuid.uuid4()),
			label=obj.label,
			web_path=obj.web_path,
		)
		self._session.add(people_table)
		self._session.commit()
		return PeopleModel(id=people_table.id, label=people_table.label, web_path=people_table.web_path)