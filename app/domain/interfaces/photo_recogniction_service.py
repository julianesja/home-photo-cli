from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Dict, List


class PhotoRecognictionService(ABC):
    @abstractmethod 
    def recognize_faces(self) -> List[Dict[str, Any]]:
        pass
    @abstractmethod
    def get_faces_images(self) -> List[bytes]:
        pass


    @abstractmethod
    def to_webp(self, quality: int = 90) -> tuple[bool, BytesIO | None, str ]:
        pass