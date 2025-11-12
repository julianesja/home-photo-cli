from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.interfaces.embedding_service import EmbeddingService
from app.domain.interfaces.extension_service import ExtensionService
from app.domain.interfaces.hashing_service import HashingService
from app.domain.repositories.photo_repository import PhotoRepository
from app.domain.repositories.storage_repository import StorageRepository
from app.domain.repositories.vector_repository import VectorRepository
from app.domain.repositories.duplicate_photo_repository import DuplicatePhotoRepository
from app.domain.repositories.people_repository import PeopleRepository
from app.domain.repositories.photo_people_repository import PhotoPeopleRepository
from app.domain.interfaces.photo_recogniction_service import PhotoRecognictionService

from app.infrastructure.repositories.photo_repository_orm import PhotoRepositoryORM
from app.infrastructure.repositories.storage_repository_minio import StorageRepositoryMinio
from app.infrastructure.repositories.vector_db_qdrant import VectorDBQdrant
from app.infrastructure.services.embedding_service_imple import EmbeddingServiceImpl
from app.infrastructure.services.extension_service_imple import ExtensionServiceImpl
from app.infrastructure.services.hashing_service_imple import HashingServiceImpl
from app.infrastructure.repositories.duplicate_photo_repository_orm import DuplicatePhotoRepositoryORM
from app.infrastructure.services.photo_recogniction_service_imple import PhotoRecognictionServiceImpl
from app.infrastructure.repositories.people_repository_orm import PeopleRepositoryORM
from app.infrastructure.repositories.photo_people_repository_orm import PhotoPeopleRepositoryORM

from app.config.settings import Settings

from app.application.use_cases.process_photo import ProcessPhoto


def cli_main(file_path: str):
    file_content = open(file_path, "rb").read()
    config = Settings()
    engine = create_engine(
        config.db_url
        )
    session_local = sessionmaker(bind=engine)
    session = session_local()

    hashing_service: HashingService = HashingServiceImpl()
    photo_repository: PhotoRepository = PhotoRepositoryORM(session)
    storage_repository: StorageRepository = StorageRepositoryMinio(
        endpoint=config.minio_endpoint,
        access_key=config.minio_access_key,
        secret_key=config.minio_secret_key,
        bucket_name=config.minio_bucket_name,
        secure=config.minio_secure)
    extension_service: ExtensionService = ExtensionServiceImpl()
    
    embedding_service: EmbeddingService = EmbeddingServiceImpl(model_name=config.embedding_model_name)
    photo_vector_repository: VectorRepository = VectorDBQdrant(
        collection_name="photo_vectors",
        vector_size=config.vector_size_photo,
        distance=config.distance)
    people_vector_repository: VectorRepository = VectorDBQdrant(
        collection_name="people_vectors",
        vector_size=config.vector_size_people,
        distance=config.distance)
    
    duplicate_repository: DuplicatePhotoRepository = DuplicatePhotoRepositoryORM(session)
    photo_recogniction_service: PhotoRecognictionService = PhotoRecognictionServiceImpl(file_content,extension_service)
    people_repository: PeopleRepository = PeopleRepositoryORM(session)
    people_storage_repository: StorageRepository = StorageRepositoryMinio(
        endpoint=config.minio_endpoint,
        access_key=config.minio_access_key,
        secret_key=config.minio_secret_key,
        bucket_name=config.minio_bucket_name,
        secure=config.minio_secure)
    photo_people_repository: PhotoPeopleRepository = PhotoPeopleRepositoryORM(session)
    process_photo: ProcessPhoto = ProcessPhoto(
        hashing_service=hashing_service,
        photo_repository=photo_repository,
        storage_repository=storage_repository,
        extension_service=extension_service,
        embedding_service=embedding_service,
        photo_vector_repository=photo_vector_repository,
        people_vector_repository=people_vector_repository,
        duplicate_repository=duplicate_repository,
        photo_recogniction_service=photo_recogniction_service,
        people_repository=people_repository,
        people_storage_repository=people_storage_repository,
        photo_people_repository=photo_people_repository)
    
    #result, photo, error = process_photo.execute(file_content)
    resultado = process_photo.execute(file_content)
    print(f"Resultado: {resultado}")
    #if not result:
    #    print(f"Error al procesar la foto: {error}")
    #    return
    #print(f"Foto procesada correctamente: {photo.id}")