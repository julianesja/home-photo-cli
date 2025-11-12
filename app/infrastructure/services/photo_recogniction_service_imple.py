from io import BytesIO
from typing import Any, Dict, List
from app.domain.interfaces.extension_service import ExtensionService
from app.domain.interfaces.photo_recogniction_service import PhotoRecognictionService
import numpy as np
import pillow_heif
from PIL import Image
import face_recognition


class PhotoRecognictionServiceImpl(PhotoRecognictionService):

    def __init__(self,
    file_content: bytes,
    extension_service: ExtensionService):
        self.file_content = file_content
        self.extension_service = extension_service
    
    def recognize_faces(self) -> List[Dict[str, Any]]:
        try:
            extension = self.extension_service.get_file_extension_from_bytes(self.file_content)
            if extension is None:
                return []
            if extension in {'heic', 'heif'}:
                # Procesar archivo HEIC/HEIF
                heif_file = pillow_heif.read_heif(self.file_content)
                if not heif_file.data:
                    print(f"Error: No se pudo leer el archivo HEIC ")
                    return []
                
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw"
                )
                # Convertir a RGB si es necesario
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Convertir a numpy array para face_recognition
                image_array = np.array(image)
            else:
                # Procesar otros formatos
                file_like = BytesIO(self.file_content)
                image = face_recognition.load_image_file(file_like)
                image_array = face_recognition.load_image_file(file_like)
            face_locations = face_recognition.face_locations(image_array)
            face_encodings = face_recognition.face_encodings(image_array, face_locations)

            results = []
            pil_image = Image.fromarray(image)
            for (location, encoding ) in zip(face_locations, face_encodings):
                top, right, bottom, left = face_locations
                buffer = BytesIO()
                # Recortar la cara
                face_image = pil_image.crop((left, top, right, bottom))

                # Guardar la cara recortada en memoria como bytes
                buffer = BytesIO()
                face_image.save(buffer, format="WEBP")
                
                results.append({
                    "location": location,               # (top, right, bottom, left)
                    "embedding": encoding.tolist() ,
                    "face_image": buffer.getvalue()    # Convertimos NumPy array a lista
                })

            return results
        except Exception as e:
            print(f"Error procesando archivo: {e}")
            return []

    def get_faces_images(self) -> List[bytes]:
        
        # Cargar la imagen desde bytes
        image = face_recognition.load_image_file(BytesIO(self.file_content))

        # Detectar las ubicaciones de las caras
        face_locations = face_recognition.face_locations(image)

        # Convertir a objeto PIL para recortar
        pil_image = Image.fromarray(image)

        faces_bytes = []

        for (top, right, bottom, left) in face_locations:
            # Recortar la cara
            face_image = pil_image.crop((left, top, right, bottom))

            # Guardar la cara recortada en memoria como bytes
            buffer = BytesIO()
            face_image.save(buffer, format="JPEG")
            faces_bytes.append(buffer.getvalue())

        return faces_bytes

    def to_webp(self, quality: int = 90) -> tuple[bool, BytesIO | None, str ]:
        try:
            # Verificar si es un archivo HEIC/HEIF por los primeros bytes
            extension = self.extension_service.get_file_extension_from_bytes(self.file_content)
            if extension in {'heic', 'heif'}:
                # Es un archivo HEIC/HEIF
                heif_file = pillow_heif.read_heif(self.file_content)
                if not heif_file.data:
                    return False, None, "HEIF file no tiene datos de imagen válidos"
                
                img = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw"
                )
            else:
                # Es un formato estándar (JPEG, PNG, etc.)
                img = Image.open(BytesIO(self.file_content))
            
            # Normalizamos a RGB si la imagen tiene transparencia o paleta
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            output = BytesIO()
            img.save(output, format="WEBP", quality=quality)
            output.seek(0)
            return True, output, ""
            
        except Exception as e:
            return False, None, f"Error al convertir a WebP ${e}"