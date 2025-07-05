from app.db.repositories.base_repository import BaseRepository
from app.db.models import PhotoPeople, Photo, Person
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

class PhotoPeopleRepository(BaseRepository[PhotoPeople]):
    def __init__(self, session: Session):
        super().__init__(PhotoPeople, session)

    def get_by_photo(self, photo_id: int) -> List[PhotoPeople]:
        """Obtiene todas las relaciones de una foto específica."""
        return self.session.query(self.model).filter_by(photo_id=photo_id).all()

    def get_by_person(self, person_id: int) -> List[PhotoPeople]:
        """Obtiene todas las relaciones de una persona específica."""
        return self.session.query(self.model).filter_by(person_id=person_id).all()

    def get_people_by_photo(self, photo_id: int) -> List[Person]:
        """Obtiene todas las personas que aparecen en una foto."""
        return self.session.query(Person).join(PhotoPeople).filter(
            PhotoPeople.photo_id == photo_id
        ).all()

    def get_photos_by_person(self, person_id: int) -> List[Photo]:
        """Obtiene todas las fotos donde aparece una persona."""
        return self.session.query(Photo).join(PhotoPeople).filter(
            PhotoPeople.person_id == person_id
        ).all()

    def create_relationship(self, photo_id: int, person_id: int) -> PhotoPeople:
        """Crea una nueva relación entre foto y persona."""
        relationship = PhotoPeople(photo_id=photo_id, person_id=person_id)
        self.session.add(relationship)
        self.session.commit()
        self.session.refresh(relationship)
        return relationship

    def delete_relationship(self, photo_id: int, person_id: int) -> bool:
        """Elimina una relación específica entre foto y persona."""
        relationship = self.session.query(self.model).filter_by(
            photo_id=photo_id, person_id=person_id
        ).first()
        
        if not relationship:
            return False
        
        self.session.delete(relationship)
        self.session.commit()
        return True

    def delete_by_photo(self, photo_id: int) -> int:
        """Elimina todas las relaciones de una foto y retorna el número eliminado."""
        relationships = self.get_by_photo(photo_id)
        count = len(relationships)
        for relationship in relationships:
            self.session.delete(relationship)
        self.session.commit()
        return count

    def delete_by_person(self, person_id: int) -> int:
        """Elimina todas las relaciones de una persona y retorna el número eliminado."""
        relationships = self.get_by_person(person_id)
        count = len(relationships)
        for relationship in relationships:
            self.session.delete(relationship)
        self.session.commit()
        return count

    def get_people_count_by_photo(self, photo_id: int) -> int:
        """Obtiene el número de personas en una foto."""
        return self.session.query(func.count(self.model.person_id)).filter_by(
            photo_id=photo_id
        ).scalar()

    def get_photos_count_by_person(self, person_id: int) -> int:
        """Obtiene el número de fotos donde aparece una persona."""
        return self.session.query(func.count(self.model.photo_id)).filter_by(
            person_id=person_id
        ).scalar()

    def get_photos_with_people_count(self):
        """Obtiene todas las fotos con el conteo de personas."""
        return self.session.query(
            Photo,
            func.count(self.model.person_id).label('people_count')
        ).outerjoin(self.model).group_by(Photo.id).all()

    def get_people_with_photos_count(self):
        """Obtiene todas las personas con el conteo de fotos."""
        return self.session.query(
            Person,
            func.count(self.model.photo_id).label('photos_count')
        ).outerjoin(self.model).group_by(Person.id).all()

    def exists_relationship(self, photo_id: int, person_id: int) -> bool:
        """Verifica si existe una relación entre foto y persona."""
        return self.session.query(self.model).filter_by(
            photo_id=photo_id, person_id=person_id
        ).first() is not None

    def get_photos_with_people_info(self):
        """Obtiene fotos con información de las personas que aparecen."""
        return self.session.query(
            Photo,
            func.group_concat(Person.label).label('people_labels')
        ).join(self.model).join(Person).group_by(Photo.id).all()

    def get_people_with_photos_info(self):
        """Obtiene personas con información de las fotos donde aparecen."""
        return self.session.query(
            Person,
            func.group_concat(Photo.filename).label('photo_filenames')
        ).join(self.model).join(Photo).group_by(Person.id).all() 