import face_recognition
from PIL import Image
import numpy as np
from typing import List, Dict, Any
import pillow_heif
from pathlib import Path

def detect_faces_and_embeddings(image_path: str) -> List[Dict[str, Any]]:
    """
    Detecta rostros en una imagen y retorna sus ubicaciones y embeddings.

    :param image_path: Ruta absoluta de la imagen.
    :return: List[Dict] con cada rostro encontrado y su embedding.
    """
    try:
        # Abrir imagen según el formato
        image_path_obj = Path(image_path)
        
        if image_path_obj.suffix.lower() in {'.heic', '.heif'}:
            # Procesar archivo HEIC/HEIF
            heif_file = pillow_heif.read_heif(str(image_path_obj))
            if not heif_file.data:
                print(f"Error: No se pudo leer el archivo HEIC {image_path}")
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
            image_array = face_recognition.load_image_file(image_path)
        
        face_locations = face_recognition.face_locations(image_array)
        face_encodings = face_recognition.face_encodings(image_array, face_locations)

        results = []
        for location, encoding in zip(face_locations, face_encodings):
            results.append({
                "location": location,               # (top, right, bottom, left)
                "embedding": encoding.tolist()      # Convertimos NumPy array a lista
            })

        return results

    except Exception as e:
        print(f"Error procesando {image_path}: {e}")
        return []
