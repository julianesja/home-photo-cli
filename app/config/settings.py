"""Application configuration using Pydantic BaseSettings."""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Set

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # project root


class Settings(BaseSettings):
    """Configuration values loaded from environment variables or .env file."""

    # Database Configuration
    db_url: str = Field(
        default=os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'homephoto.db'}"),
        description="Database connection URL"
    )
    
    # Image Processing Configuration
    image_folder: str = Field(
        default=os.getenv("IMAGE_FOLDER", "./images"),
        description="Path to the folder containing images to process"
    )
    batch_size: int = Field(
        default=int(os.getenv("BATCH_SIZE", "32")),
        description="Batch size for processing images"
    )
    
    # MinIO Configuration
    minio_endpoint: str = Field(
        default=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        description="MinIO server endpoint"
    )
    minio_access_key: str = Field(
        default=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        description="MinIO access key"
    )
    minio_secret_key: str = Field(
        default=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        description="MinIO secret key"
    )
    minio_bucket_name: str = Field(
        default=os.getenv("MINIO_BUCKET_NAME", "fotos"),
        description="MinIO bucket name for storing photos"
    )
    minio_secure: bool = Field(
        default=os.getenv("MINIO_SECURE", "false").lower() == "true",
        description="Whether to use HTTPS for MinIO connection"
    )
    
    # Face Recognition Configuration
    face_recognition_tolerance: float = Field(
        default=float(os.getenv("FACE_RECOGNITION_TOLERANCE", "0.6")),
        description="Tolerance for face recognition matching"
    )
    face_recognition_model: str = Field(
        default=os.getenv("FACE_RECOGNITION_MODEL", "hog"),
        description="Face recognition model to use (hog or cnn)"
    )
    
    # Duplicate Detection Configuration
    duplicate_threshold: int = Field(
        default=int(os.getenv("DUPLICATE_THRESHOLD", "10")),
        description="Threshold for duplicate detection"
    )
    hash_size: int = Field(
        default=int(os.getenv("HASH_SIZE", "8")),
        description="Hash size for image hashing"
    )
    
    # Supported Image Extensions
    supported_extensions: Set[str] = Field(
        default=set(os.getenv("SUPPORTED_EXTENSIONS", ".jpg,.jpeg,.png,.bmp,.tiff,.webp,.heic,.heif").split(",")),
        description="Set of supported image file extensions"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="Logging level"
    )
    log_format: str = Field(
        default=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        description="Logging format string"
    )
    
    # Development Settings
    debug: bool = Field(
        default=os.getenv("DEBUG", "false").lower() == "true",
        description="Enable debug mode"
    )

    embedding_model_name: str = Field(
        default=os.getenv("EMBEDDING_MODEL_NAME", "clip-ViT-B-32"),
        description="Name of the embedding model to use"
    )

    vector_size_photo: int = Field(
        default=int(os.getenv("VECTOR_SIZE_PHOTO", "512")),
        description="Size of the vector"
    )

    vector_size_people: int = Field(
        default=int(os.getenv("VECTOR_SIZE_PEOPLE", "128")),
        description="Size of the vector"
    )

    distance: str = Field(
        default=os.getenv("DISTANCE", "Cosine"),
        description="Distance to use for the vector"
    )
    
    
    model_config = {
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

