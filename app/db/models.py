"""
Modelos SQLAlchemy para el organizador de fotos por reconocimiento facial.
Basado en el esquema SQL definido en schema.sql
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import json
from typing import List, Optional

# Crear la base para los modelos
Base = declarative_base()

class Photo(Base):
    """
    Modelo para la tabla 'photos'.
    Representa las fotos procesadas en el sistema.
    """
    __tablename__ = 'photos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    path = Column(Text, nullable=False)
    hash = Column(String(64), nullable=False, unique=True)  # SHA256
    phash = Column(String(32), nullable=True)  # Hash perceptual (pHash)
    processed_at = Column(DateTime, default=func.now())
    is_new = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    people = relationship("PhotoPeople", back_populates="photo", cascade="all, delete-orphan")
    face_embeddings = relationship("FaceEmbedding", back_populates="photo", cascade="all, delete-orphan")
    duplicates_as_original = relationship("Duplicate", foreign_keys="Duplicate.duplicate_of_id", back_populates="original_photo")
    duplicates_as_duplicate = relationship("Duplicate", foreign_keys="Duplicate.photo_id", back_populates="duplicate_photo")
    
    def __repr__(self):
        return f"<Photo(id={self.id}, filename='{self.filename}', hash='{self.hash[:8]}...')>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        processed_at = getattr(self, 'processed_at', None)
        return {
            'id': self.id,
            'filename': self.filename,
            'path': self.path,
            'hash': self.hash,
            'phash': self.phash,
            'is_new': self.is_new,
            'processed_at': processed_at.isoformat() if processed_at else None
        }

class Person(Base):
    """
    Modelo para la tabla 'people'.
    Representa las personas detectadas en las fotos.
    """
    __tablename__ = 'people'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String(100), nullable=False)  # Ej: "Persona 1", "Persona 2"
    avg_embedding = Column(Text)  # Vector promedio serializado (JSON)
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    photos = relationship("PhotoPeople", back_populates="person", cascade="all, delete-orphan")
    face_embeddings = relationship("FaceEmbedding", back_populates="person", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Person(id={self.id}, label='{self.label}')>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        created_at = getattr(self, 'created_at', None)
        return {
            'id': self.id,
            'label': self.label,
            'avg_embedding': self.avg_embedding,
            'created_at': created_at.isoformat() if created_at else None
        }
    
    def get_avg_embedding_array(self) -> Optional[List[float]]:
        """Obtiene el embedding promedio como lista de floats."""
        avg_embedding = getattr(self, 'avg_embedding', None)
        if avg_embedding:
            try:
                return json.loads(str(avg_embedding))
            except json.JSONDecodeError:
                return None
        return None
    
    def set_avg_embedding_array(self, embedding: List[float]):
        """Establece el embedding promedio desde una lista de floats."""
        self.avg_embedding = json.dumps(embedding)

class PhotoPeople(Base):
    """
    Modelo para la tabla 'photo_people'.
    Tabla de relación N:M entre fotos y personas.
    """
    __tablename__ = 'photo_people'
    
    photo_id = Column(Integer, ForeignKey('photos.id', ondelete='CASCADE'), primary_key=True)
    person_id = Column(Integer, ForeignKey('people.id', ondelete='CASCADE'), primary_key=True)
    
    # Relaciones
    photo = relationship("Photo", back_populates="people")
    person = relationship("Person", back_populates="photos")
    
    def __repr__(self):
        return f"<PhotoPeople(photo_id={self.photo_id}, person_id={self.person_id})>"

class FaceEmbedding(Base):
    """
    Modelo para la tabla 'face_embeddings'.
    Representa los embeddings individuales por rostro detectado.
    """
    __tablename__ = 'face_embeddings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('people.id', ondelete='CASCADE'), nullable=False)
    photo_id = Column(Integer, ForeignKey('photos.id', ondelete='CASCADE'), nullable=False)
    embedding = Column(Text, nullable=False)  # Vector facial como arreglo JSON
    
    # Relaciones
    person = relationship("Person", back_populates="face_embeddings")
    photo = relationship("Photo", back_populates="face_embeddings")
    
    def __repr__(self):
        return f"<FaceEmbedding(id={self.id}, person_id={self.person_id}, photo_id={self.photo_id})>"
    
    def get_embedding_array(self) -> List[float]:
        """Obtiene el embedding como lista de floats."""
        embedding = getattr(self, 'embedding', None)
        if embedding:
            try:
                return json.loads(str(embedding))
            except json.JSONDecodeError:
                return []
        return []
    
    def set_embedding_array(self, embedding: List[float]):
        """Establece el embedding desde una lista de floats."""
        self.embedding = json.dumps(embedding)
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'person_id': self.person_id,
            'photo_id': self.photo_id,
            'embedding': self.embedding
        }

class Duplicate(Base):
    """
    Modelo para la tabla 'duplicates'.
    Registro de imágenes duplicadas.
    """
    __tablename__ = 'duplicates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    photo_id = Column(Integer, ForeignKey('photos.id', ondelete='CASCADE'), nullable=False)
    duplicate_of_id = Column(Integer, ForeignKey('photos.id', ondelete='CASCADE'), nullable=False)
    reason = Column(String(100))  # Ej: "hash", "visual_embedding"
    
    # Relaciones
    original_photo = relationship("Photo", foreign_keys=[duplicate_of_id], back_populates="duplicates_as_original")
    duplicate_photo = relationship("Photo", foreign_keys=[photo_id], back_populates="duplicates_as_duplicate")
    
    # Constraint único
    __table_args__ = (
        UniqueConstraint('photo_id', 'duplicate_of_id', name='uq_photo_duplicate'),
    )
    
    def __repr__(self):
        return f"<Duplicate(id={self.id}, photo_id={self.photo_id}, duplicate_of_id={self.duplicate_of_id}, reason='{self.reason}')>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'photo_id': self.photo_id,
            'duplicate_of_id': self.duplicate_of_id,
            'reason': self.reason
        }

# Funciones de utilidad para trabajar con los modelos

def create_tables(engine):
    """Crea todas las tablas en la base de datos."""
    Base.metadata.create_all(engine)

def drop_tables(engine):
    """Elimina todas las tablas de la base de datos."""
    Base.metadata.drop_all(engine)

def get_session(engine):
    """Crea y retorna una sesión de SQLAlchemy."""
    Session = sessionmaker(bind=engine)
    return Session()

    """
    Consulta todos los duplicados de una foto específica.
    
    Args:
        session: Sesión de SQLAlchemy
        photo_id: ID de la foto
        
    Returns:
        Lista de objetos Duplicate
    """
    return session.query(Duplicate).filter(Duplicate.photo_id == photo_id).all() 