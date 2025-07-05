from app.db.repositories.base_repository import BaseRepository
from app.db.models import Duplicate, Photo
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

class DuplicateRepository(BaseRepository[Duplicate]):
    def __init__(self, session: Session):
        super().__init__(Duplicate, session)

    def get_by_photo(self, photo_id: int) -> List[Duplicate]:
        """Obtiene todos los duplicados de una foto específica."""
        return self.session.query(self.model).filter_by(photo_id=photo_id).all()

    def get_by_original(self, original_photo_id: int) -> List[Duplicate]:
        """Obtiene todos los duplicados de una foto original."""
        return self.session.query(self.model).filter_by(duplicate_of_id=original_photo_id).all()

    def get_duplicates_by_reason(self, reason: str) -> List[Duplicate]:
        """Obtiene todos los duplicados por una razón específica."""
        return self.session.query(self.model).filter_by(reason=reason).all()

    def create_duplicate(self, photo_id: int, duplicate_of_id: int, reason: str) -> Duplicate:
        """Crea un nuevo registro de duplicado."""
        duplicate = Duplicate(
            photo_id=photo_id,
            duplicate_of_id=duplicate_of_id,
            reason=reason
        )
        self.session.add(duplicate)
        self.session.commit()
        self.session.refresh(duplicate)
        return duplicate

    def delete_by_photo(self, photo_id: int) -> int:
        """Elimina todos los duplicados de una foto y retorna el número eliminado."""
        duplicates = self.get_by_photo(photo_id)
        count = len(duplicates)
        for duplicate in duplicates:
            self.session.delete(duplicate)
        self.session.commit()
        return count

    def delete_by_original(self, original_photo_id: int) -> int:
        """Elimina todos los duplicados de una foto original y retorna el número eliminado."""
        duplicates = self.get_by_original(original_photo_id)
        count = len(duplicates)
        for duplicate in duplicates:
            self.session.delete(duplicate)
        self.session.commit()
        return count

    def get_duplicates_count(self, photo_id: int) -> int:
        """Obtiene el número de duplicados de una foto."""
        return self.session.query(func.count(self.model.id)).filter_by(photo_id=photo_id).scalar()

    def get_duplicates_count_by_original(self, original_photo_id: int) -> int:
        """Obtiene el número de duplicados de una foto original."""
        return self.session.query(func.count(self.model.id)).filter_by(duplicate_of_id=original_photo_id).scalar()

    def get_duplicates_by_reason_count(self, reason: str) -> int:
        """Obtiene el número de duplicados por razón."""
        return self.session.query(func.count(self.model.id)).filter_by(reason=reason).scalar()

    def get_duplicates_with_photo_info(self, photo_id: int):
        """Obtiene duplicados con información de la foto original."""
        return self.session.query(
            self.model,
            Photo.filename.label('original_filename'),
            Photo.path.label('original_path')
        ).join(Photo, self.model.duplicate_of_id == Photo.id).filter_by(photo_id=photo_id).all()

    def get_duplicates_with_duplicate_info(self, original_photo_id: int):
        """Obtiene duplicados con información de la foto duplicada."""
        return self.session.query(
            self.model,
            Photo.filename.label('duplicate_filename'),
            Photo.path.label('duplicate_path')
        ).join(Photo, self.model.photo_id == Photo.id).filter_by(duplicate_of_id=original_photo_id).all()

    def get_duplicates_summary(self):
        """Obtiene un resumen de duplicados por razón."""
        return self.session.query(
            self.model.reason,
            func.count(self.model.id).label('count')
        ).group_by(self.model.reason).all()

    def get_photos_with_duplicates_count(self):
        """Obtiene fotos con el conteo de sus duplicados."""
        return self.session.query(
            Photo,
            func.count(self.model.id).label('duplicates_count')
        ).outerjoin(self.model, Photo.id == self.model.photo_id).group_by(Photo.id).all()

    def get_original_photos_with_duplicates_count(self):
        """Obtiene fotos originales con el conteo de duplicados que generan."""
        return self.session.query(
            Photo,
            func.count(self.model.id).label('duplicates_generated')
        ).outerjoin(self.model, Photo.id == self.model.duplicate_of_id).group_by(Photo.id).all()

    def exists_duplicate(self, photo_id: int, duplicate_of_id: int) -> bool:
        """Verifica si existe un duplicado específico."""
        return self.session.query(self.model).filter_by(
            photo_id=photo_id, duplicate_of_id=duplicate_of_id
        ).first() is not None

    def get_duplicate_chains(self):
        """
        Obtiene cadenas de duplicados (fotos que son duplicados de duplicados).
        Retorna una lista de cadenas donde cada cadena es una lista de IDs de fotos.
        """
        # Esta es una implementación básica. Para casos complejos, considera usar CTEs
        all_duplicates = self.list_all()
        chains = []
        processed = set()
        
        for duplicate in all_duplicates:
            if duplicate.photo_id in processed:
                continue
                
            chain = [duplicate.photo_id]
            current_duplicate = duplicate
            
            # Seguir la cadena hacia arriba
            while current_duplicate:
                processed.add(current_duplicate.photo_id)
                next_duplicate = self.session.query(self.model).filter_by(
                    photo_id=current_duplicate.duplicate_of_id
                ).first()
                
                if next_duplicate:
                    chain.append(next_duplicate.photo_id)
                    current_duplicate = next_duplicate
                else:
                    chain.append(current_duplicate.duplicate_of_id)
                    break
            
            if len(chain) > 1:
                chains.append(chain)
        
        return chains

    def get_duplicate_groups(self):
        """
        Agrupa duplicados por su foto original más alta en la cadena.
        Retorna un diccionario donde la clave es el ID de la foto original
        y el valor es una lista de IDs de fotos duplicadas.
        """
        chains = self.get_duplicate_chains()
        groups = {}
        
        for chain in chains:
            original_id = chain[-1]  # El último en la cadena es el original
            duplicate_ids = chain[:-1]  # Todos excepto el último son duplicados
            
            if original_id not in groups:
                groups[original_id] = []
            
            groups[original_id].extend(duplicate_ids)
        
        return groups 