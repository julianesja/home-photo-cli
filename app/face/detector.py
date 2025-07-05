import face_recognition
from PIL import Image
import numpy as np
from typing import List, Dict, Any

def detect_faces_and_embeddings(image_path: str) -> List[Dict[str, Any]]:
    """
    Detecta rostros en una imagen y retorna sus ubicaciones y embeddings.

    :param image_path: Ruta absoluta de la imagen.
    :return: List[Dict] con cada rostro encontrado y su embedding.
    """
    try:
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

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
