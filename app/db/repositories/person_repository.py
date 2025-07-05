from app.db.repositories.base_repository import BaseRepository
from app.db.models import Person, PhotoPeople, FaceEmbedding
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func, and_

class PersonRepository(BaseRepository[Person]):
    def __init__(self, session: Session):
        super().__init__(Person, session)

    def get_by_label(self, label: str) -> Optional[Person]:
        """Obtiene una persona por su etiqueta."""
        return self.session.query(self.model).filter_by(label=label).first()

    def get_with_photos(self, person_id: int) -> Optional[Person]:
        """Obtiene una persona con todas sus fotos relacionadas."""
        return self.session.query(self.model).filter_by(id=person_id).first()

    def get_photos_count(self, person_id: int) -> int:
        """Obtiene el número de fotos donde aparece una persona."""
        return self.session.query(func.count(PhotoPeople.photo_id)).filter(
            PhotoPeople.person_id == person_id
        ).scalar()

    def get_people_with_photo_count(self):
        """Obtiene todas las personas con el conteo de sus fotos."""
        return self.session.query(
            self.model,
            func.count(PhotoPeople.photo_id).label('photo_count')
        ).outerjoin(PhotoPeople).group_by(self.model.id).all()

    def get_people_by_photo(self, photo_id: int) -> List[Person]:
        """Obtiene todas las personas que aparecen en una foto específica."""
        return self.session.query(self.model).join(PhotoPeople).filter(
            PhotoPeople.photo_id == photo_id
        ).all()

    def get_embeddings(self, person_id: int) -> List[FaceEmbedding]:
        """Obtiene todos los embeddings faciales de una persona."""
        return self.session.query(FaceEmbedding).filter_by(person_id=person_id).all()

    def update_avg_embedding(self, person_id: int, avg_embedding: List[float]) -> bool:
        """Actualiza el embedding promedio de una persona."""
        person = self.get(person_id)
        if not person:
            return False
        
        person.set_avg_embedding_array(avg_embedding)
        self.session.commit()
        return True

    def get_people_with_embeddings(self) -> List[Person]:
        """Obtiene todas las personas que tienen embeddings promedio."""
        people = self.list_all()
        return [person for person in people if getattr(person, 'avg_embedding', None)]

    def get_next_label(self) -> str:
        """Genera la siguiente etiqueta disponible para una persona."""
        last_person = self.session.query(self.model).order_by(
            self.model.id.desc()
        ).first()
        
        if not last_person:
            return "Persona 1"
        
        # Extraer número de la última etiqueta
        try:
            last_number = int(last_person.label.split()[-1])
            return f"Persona {last_number + 1}"
        except (ValueError, IndexError):
            return "Persona 1" 