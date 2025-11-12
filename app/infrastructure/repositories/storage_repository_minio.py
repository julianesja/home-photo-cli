from app.domain.repositories.storage_repository import StorageRepository
import io
import uuid
from minio import Minio
from app.config.settings import Settings

class StorageRepositoryMinio(StorageRepository):
    """Repositorio para manejar operaciones con MinIO bucket"""
    
    def __init__(self, endpoint: str = None, 
                 access_key: str = None, 
                 secret_key: str = None, 
                 bucket_name: str = None,
                 secure: bool = None):
        """
        Inicializa el repositorio y crea el bucket si no existe
        
        Args:
            endpoint: Endpoint del servidor MinIO (opcional, usa settings si no se proporciona)
            access_key: Clave de acceso (opcional, usa settings si no se proporciona)
            secret_key: Clave secreta (opcional, usa settings si no se proporciona)
            bucket_name: Nombre del bucket (opcional, usa settings si no se proporciona)
            secure: Si usar HTTPS (opcional, usa settings si no se proporciona)
        """
        settings = Settings()
        self.client = Minio(
            endpoint or settings.minio_endpoint,
            access_key=access_key or settings.minio_access_key,
            secret_key=secret_key or settings.minio_secret_key,
            secure=secure if secure is not None else settings.minio_secure
        )
        self.bucket_name = bucket_name or settings.minio_bucket_name
        self._init_bucket()
    
    def _init_bucket(self):
        """Crea el bucket si no existe"""
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            print(f"✅ Bucket '{self.bucket_name}' creado")
        else:
            print(f"ℹ️  Bucket '{self.bucket_name}' ya existe")
    
    def upload_file(self, file_bytes: bytes, extension: str, content_type: str = "image/jpeg") -> tuple[bool, str, str]:
        try:
            object_name = f"{uuid.uuid4()}.{extension}"
            file_stream = io.BytesIO(file_bytes) 
            self.client.put_object(
                self.bucket_name,
                object_name,
                data=file_stream,
                length=len(file_bytes),
                content_type=content_type
            )
            return True, object_name, ""
        except Exception as e:
            return False, "", f"No se pudo subir el archivo a MinIO {e}"