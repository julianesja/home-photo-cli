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
    __tablename__ = 'photo'
    
    
    id = Column(String(36), primary_key=True)
    path = Column(Text)
    path_web = Column(Text)
    hash = Column(String(64))
    
    # Relaciones
    people = relationship("PhotoPeople", back_populates="photo", cascade="all, delete-orphan")
    
    duplicates_as_original = relationship("Duplicate", foreign_keys="Duplicate.duplicate_of_id", back_populates="original_photo")
    duplicates_as_duplicate = relationship("Duplicate", foreign_keys="Duplicate.photo_id", back_populates="duplicate_photo")
    
    def __repr__(self):
        return f"<Photo(id={self.id}, filename='{self.filename}', web_path='{self.web_path}', hash='{self.hash[:8]}...')>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'path': self.path,
            'web_path': self.web_path,
            'hash': self.hash,
        }

class People(Base):
    """
    Modelo para la tabla 'people'.
    Representa las personas detectadas en las fotos.
    """
    __tablename__ = 'people'
    
    id = Column(String(36), primary_key=True)
    nombre = Column(String(36), nullable=False)
    path_web = Column(Text)
    
    # Relaciones
    photos = relationship("PhotoPeople", back_populates="people", cascade="all, delete-orphan")
    
    
    def __repr__(self):
        return f"<people(id={self.id}, label='{self.label}')>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'label': self.label,
            'web_path': self.web_path,
        }

class PhotoPeople(Base):
    """
    Modelo para la tabla 'photo_people'.
    Tabla de relación N:M entre fotos y personas.
    """
    __tablename__ = 'photo_people'
    
    people_id = Column(String(36), ForeignKey('people.id', ondelete='CASCADE'), primary_key=True)
    photo_id = Column(String(36), ForeignKey('photo.id', ondelete='CASCADE'), primary_key=True)
    
    # Relaciones
    people = relationship("People", back_populates="photos")
    photo = relationship("Photo", back_populates="people")
    
    def __repr__(self):
        return f"<PhotoPeople(photo_id={self.photo_id}, people_id={self.person_id})>"

class Duplicate(Base):
    """
    Modelo para la tabla 'duplicates'.
    Registro de imágenes duplicadas.
    """
    __tablename__ = 'duplicates'
    
    photo_id = Column(Text, ForeignKey('photo.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    duplicate_of_id = Column(Text, ForeignKey('photo.id', ondelete='CASCADE'), nullable=False, primary_key=True)
     
    # Relaciones
    original_photo = relationship("Photo", foreign_keys=[duplicate_of_id], back_populates="duplicates_as_original")
    duplicate_photo = relationship("Photo", foreign_keys=[photo_id], back_populates="duplicates_as_duplicate")
    
    # Constraint único
    __table_args__ = (
        UniqueConstraint('photo_id', 'duplicate_of_id', name='uq_photo_duplicate'),
    )
    
    def __repr__(self):
        return f"<Duplicate(photo_id={self.photo_id}, duplicate_of_id={self.duplicate_of_id})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'photo_id': self.photo_id,
            'duplicate_of_id': self.duplicate_of_id,
        }
