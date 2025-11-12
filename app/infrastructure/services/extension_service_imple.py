import filetype
from app.domain.interfaces.extension_service import ExtensionService

class ExtensionServiceImpl(ExtensionService):

    def get_file_extension_from_bytes(self, file_content: bytes) -> str | None:
        return filetype.guess_extension(file_content)

    def get_mime_type_from_bytes(self, file_content: bytes) -> str | None:
        return filetype.guess_mime(file_content)