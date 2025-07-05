# core/processor.py

from app.face.detector import detect_faces_and_embeddings

def process_image(image_path: str):
    """
    Procesa una imagen individual: detecta rostros y embeddings.

    :param image_path: Ruta del archivo.
    :return: Diccionario con metadata de la imagen procesada.
    """
    print(f"Procesando imagen: {image_path}")
    results = detect_faces_and_embeddings(image_path)

    return {
        "image_path": image_path,
        "faces_detected": len(results),
        "faces": results
    }
