import os
import sys
from app.image.loader import load_images_from_folder

def main():
    # Configuración quemada para el procesamiento por lotes
    ROOT_FOLDER = "/Users/jestradajara/Pictures"  # Carpeta con las imágenes
    BATCH_SIZE = 100  # Número de imágenes a procesar por lote
    
    # Ejecutar la tarea IMG-02: Procesamiento por lotes
    images = load_images_from_folder(ROOT_FOLDER, batch_size=BATCH_SIZE)
    
    print(f"Total de imágenes procesadas: {len(images)}")

if __name__ == "__main__":
    main()

