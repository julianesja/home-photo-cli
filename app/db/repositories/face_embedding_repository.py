from app.db.repositories.base_repository import BaseRepository
from app.db.models import FaceEmbedding, Person, Photo
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
import numpy as np

class FaceEmbeddingRepository(BaseRepository[FaceEmbedding]):
    def __init__(self, session: Session):
        super().__init__(FaceEmbedding, session)

    def get_by_person(self, person_id: int) -> List[FaceEmbedding]:
        """Obtiene todos los embeddings de una persona específica."""
        return self.session.query(self.model).filter_by(person_id=person_id).all()

    def get_by_photo(self, photo_id: int) -> List[FaceEmbedding]:
        """Obtiene todos los embeddings de una foto específica."""
        return self.session.query(self.model).filter_by(photo_id=photo_id).all()

    def get_by_person_and_photo(self, person_id: int, photo_id: int) -> List[FaceEmbedding]:
        """Obtiene embeddings específicos de una persona en una foto."""
        return self.session.query(self.model).filter_by(
            person_id=person_id, photo_id=photo_id
        ).all()

    def get_embeddings_arrays(self, person_id: int) -> List[List[float]]:
        """Obtiene todos los embeddings de una persona como arrays de floats."""
        embeddings = self.get_by_person(person_id)
        return [emb.get_embedding_array() for emb in embeddings]

    def get_embeddings_arrays_by_photo(self, photo_id: int) -> List[List[float]]:
        """Obtiene todos los embeddings de una foto como arrays de floats."""
        embeddings = self.get_by_photo(photo_id)
        return [emb.get_embedding_array() for emb in embeddings]

    def create_with_array(self, person_id: int, photo_id: int, embedding_array: List[float]) -> FaceEmbedding:
        """Crea un nuevo embedding desde un array de floats."""
        embedding = FaceEmbedding(person_id=person_id, photo_id=photo_id)
        embedding.set_embedding_array(embedding_array)
        
        self.session.add(embedding)
        self.session.commit()
        self.session.refresh(embedding)
        return embedding

    def get_average_embedding(self, person_id: int) -> Optional[List[float]]:
        """Calcula el embedding promedio de una persona."""
        embeddings = self.get_embeddings_arrays(person_id)
        if not embeddings:
            return None
        
        # Convertir a numpy para cálculo más eficiente
        embeddings_array = np.array(embeddings)
        avg_embedding = np.mean(embeddings_array, axis=0)
        return avg_embedding.tolist()

    def get_embeddings_count(self, person_id: int) -> int:
        """Obtiene el número de embeddings de una persona."""
        return self.session.query(func.count(self.model.id)).filter_by(person_id=person_id).scalar()

    def get_embeddings_count_by_photo(self, photo_id: int) -> int:
        """Obtiene el número de embeddings en una foto."""
        return self.session.query(func.count(self.model.id)).filter_by(photo_id=photo_id).scalar()

    def delete_by_person(self, person_id: int) -> int:
        """Elimina todos los embeddings de una persona y retorna el número eliminado."""
        embeddings = self.get_by_person(person_id)
        count = len(embeddings)
        for embedding in embeddings:
            self.session.delete(embedding)
        self.session.commit()
        return count

    def delete_by_photo(self, photo_id: int) -> int:
        """Elimina todos los embeddings de una foto y retorna el número eliminado."""
        embeddings = self.get_by_photo(photo_id)
        count = len(embeddings)
        for embedding in embeddings:
            self.session.delete(embedding)
        self.session.commit()
        return count

    def get_embeddings_with_person_info(self, photo_id: int):
        """Obtiene embeddings con información de la persona asociada."""
        return self.session.query(
            self.model, Person.label
        ).join(Person).filter_by(photo_id=photo_id).all()

    def get_embeddings_with_photo_info(self, person_id: int):
        """Obtiene embeddings con información de la foto asociada."""
        return self.session.query(
            self.model, Photo.filename, Photo.path
        ).join(Photo).filter_by(person_id=person_id).all()

    def exists_embedding(self, person_id: int, photo_id: int) -> bool:
        """Verifica si existe un embedding para una persona en una foto específica."""
        return self.session.query(self.model).filter_by(
            person_id=person_id, photo_id=photo_id
        ).first() is not None

    def find_similar_embeddings(self, target_embedding: List[float], threshold: float = 0.6) -> List[FaceEmbedding]:
        """
        Encuentra embeddings similares al target usando distancia euclidiana.
        Nota: Esta es una implementación básica. Para producción, considera usar índices vectoriales.
        """
        all_embeddings = self.list_all()
        similar_embeddings = []
        
        target_array = np.array(target_embedding)
        
        for embedding in all_embeddings:
            embedding_array = embedding.get_embedding_array()
            if embedding_array:
                distance = np.linalg.norm(target_array - np.array(embedding_array))
                if distance <= threshold:
                    similar_embeddings.append(embedding)
        
        return similar_embeddings 