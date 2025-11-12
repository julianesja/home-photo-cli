from app.domain.interfaces.embedding_service import EmbeddingService
from app.domain.interfaces.extension_service import ExtensionService
from app.domain.interfaces.hashing_service import HashingService
from app.domain.models.photo import People, Photo
from app.domain.repositories.duplicate_photo_repository import DuplicatePhotoRepository
from app.domain.repositories.people_repository import PeopleRepository
from app.domain.repositories.photo_people_repository import PhotoPeopleRepository
from app.domain.repositories.photo_repository import PhotoRepository
from app.domain.repositories.storage_repository import StorageRepository
from app.domain.repositories.vector_repository import VectorRepository
from app.infrastructure.db.models import Photo as PhotoModel, PhotoPeople
from app.domain.interfaces.photo_recogniction_service import PhotoRecognictionService


class ProcessPhoto:
    def __init__(self,
        hashing_service: HashingService,
        photo_repository: PhotoRepository,
        storage_repository: StorageRepository,
        extension_service: ExtensionService,
        embedding_service: EmbeddingService,
        photo_vector_repository: VectorRepository,
        people_vector_repository: VectorRepository,
        duplicate_repository: DuplicatePhotoRepository,
        photo_recogniction_service: PhotoRecognictionService,
        people_repository: PeopleRepository,
        people_storage_repository: StorageRepository,
        photo_people_repository: PhotoPeopleRepository):
        self.hashing_service = hashing_service
        self.photo_repository = photo_repository
        self.storage_repository = storage_repository
        self.extension_service = extension_service
        self.embedding_service = embedding_service
        self.photo_vector_repository = photo_vector_repository
        self.duplicate_repository = duplicate_repository
        self.photo_recogniction_service = photo_recogniction_service
        self.people_vector_repository = people_vector_repository
        self.people_repository = people_repository
        self.photo_people_repository = photo_people_repository
        

    def execute(self, file_content: bytes) -> tuple[bool, Photo, str]:
        hash = self.hashing_service.calculate_file_hash(file_content)
        photo = self.photo_repository.get_by_hash(hash)
        if photo:
            return False, photo
        

        extension = self.extension_service.get_file_extension_from_bytes(file_content)
        mime_type = self.extension_service.get_mime_type_from_bytes(file_content)
        if extension is None or mime_type is None:
            return False, None, "Error al obtener la extensión o el tipo MIME del archivo"
        
        result, webp_file, error = self.photo_recogniction_service.to_webp()
        if not result:
            return False, None, f"Error al convertir a WebP: {error}"
        result, storage_path, error = self.storage_repository.upload_file(file_content, extension, mime_type)
        if not result:
            return False, None, f"Error al subir la foto WebP al storage: {error}"
        
        result, webp_storage_path, error = self.storage_repository.upload_file(webp_file.getvalue(), "webp", "image/webp")
        if not result:
            return False, None, f"Error al subir el archivo WebP a la base de datos: {error}"
        
        photo = self.photo_repository.create_photo(PhotoModel(hash=hash, path=storage_path, path_web=webp_storage_path))
        if not photo:
            return False, None, f"Error al crear la foto en la base de datos"
        
        result, embedding, error = self.embedding_service.get_embedding(webp_file.getvalue())
        if not result:
            return False, None, f"Error al obtener el embedding: {error}"
        
        result, ids, error = self.photo_vector_repository.search_ids(embedding)
        if not result:
            return False, None, f"Error al buscar los IDs: {error}"
        
        "Hay photos duplicadas"
        if len(ids) > 0:
            self.duplicate_repository.save_duplicate_photo(photo.id, ids)
        else:
            self.photo_vector_repository.add_vector(embedding, photo.id)

        faces = self.photo_recogniction_service.get_faces_images()
        if len(faces) > 0:
            for face in faces:
                result, person_ids, error = self.people_vector_repository.search_ids(face.embedding)
                if not result:
                    print(f"Error al buscar el ID de la persona: {error}")
                    continue
                if len(person_ids) < 1:
                    people_path = self.self.people_storage_repository.upload_file(face.face_image, ".webp", "image/webp")
                    people = self.people_repository.create_people(People(id=person_ids[0], web_path=people_path))
                    self.people_vector_repository.add_vector(face.embedding, people.id)
                    "crear people repositorio y guardar el primer id"
                    "obtener la cara de la persona y guardarla"
                    people_id = people.id
                else:
                    people_id = person_ids[0]
                self.photo_people_repository.create_photo_people(PhotoPeople(photo_id=photo.id, people_id=people_id))

            
        return True, photo, ""