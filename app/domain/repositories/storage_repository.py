from abc import ABC, abstractmethod


class StorageRepository(ABC):
    @abstractmethod
    def upload_file(self, file_bytes: bytes, extension: str, content_type: str = "image/jpeg") -> tuple[ bool, str, str]:
        pass

    @abstractmethod
    def delete_file(self, path_name) ->tuple[bool, str]:
        pass