import os
import sys
from app.image.loader import load_images_from_folder
from app.face.cluster import process_all_faces
from app.image.duplicate_checker import check_new_photos_for_duplicates


def main():
    # Configuración quemada para el procesamiento por lotes
    ROOT_FOLDER = "/Users/jestradajara/Desktop/home_photos_test"  # Carpeta con las imágenes
    BATCH_SIZE = 100  # Número de imágenes a procesar por lote
    
    # Ejecutar la tarea IMG-02: Procesamiento por lotes
    print("📸 Tarea IMG-02: Cargando imágenes...")
    images = load_images_from_folder(ROOT_FOLDER, batch_size=BATCH_SIZE)
    
    print(f"✅ Total de imágenes cargadas: {len(images)}")
    
    # Ejecutar la tarea FACE-02: Clustering de rostros
    if images:
        print("\n👤 Tarea FACE-02: Procesando rostros...")
        face_stats = process_all_faces(images, batch_size=BATCH_SIZE)
        
        print(f"\n🎉 Procesamiento completo!")
        print(f"📊 Resumen final:")
        print(f"   📸 Imágenes procesadas: {len(images)}")
        print(f"   👤 Rostros detectados: {face_stats['faces_detected']}")
        print(f"   🎯 Clusters creados: {face_stats['clusters_created']}")
        print(f"   👤 Personas creadas: {face_stats['people_created']}")
        print(f"   🔄 Personas asignadas: {face_stats['people_matched']}")
        
    else:
        print("⚠️  No se encontraron imágenes para procesar")
     # Validar duplicados perceptuales
    print("\n🔎 Tarea DUPLICATES: Validando duplicados perceptuales...")
    check_new_photos_for_duplicates(threshold=15)
    print("✅ Validación de duplicados completada.")

if __name__ == "__main__":
    main()

