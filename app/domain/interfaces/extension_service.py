from abc import ABC, abstractmethod


class ExtensionService(ABC):
    @abstractmethod
    def get_file_extension_from_bytes(self, file_content: bytes) -> str | None:
        pass

    @abstractmethod
    def get_mime_type_from_bytes(self, file_content: bytes) -> str | None:
        pass