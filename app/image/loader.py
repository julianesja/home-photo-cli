"""
Lector recursivo de imágenes desde carpetas.
Implementa la tarea IMG-01: Leer imágenes desde carpetas múltiples
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Generator
from PIL import Image
from app.db.repositories.bucket_repository import BucketRepository
from app.image.utils import to_webp
import pillow_heif
import imagehash

# Importar configuración y repositorios
from app.config.settings import settings
from app.db.repositories import PhotoRepository, DuplicateRepository
from app.db.connection import SessionLocal

def calculate_file_hash(file_path: Path) -> str:
    """Calcula el hash SHA-256 de un archivo."""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        print(f"Error calculando hash de {file_path}: {e}")
        return ""

def calculate_phash(file_path: Path) -> str:
    """Calcula el hash perceptual (pHash) de una imagen."""
    try:
        if file_path.suffix.lower() in {'.heic', '.heif'}:
            heif_file = pillow_heif.read_heif(str(file_path))
            if not heif_file.data:
                print(f"Error: HEIF file {file_path} no tiene datos de imagen.")
                return ""
            img = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw"
            )
        else:
            img = Image.open(file_path)
        phash = imagehash.phash(img)
        return str(phash)
    except Exception as e:
        print(f"Error calculando phash de {file_path}: {e}")
        return ""

def is_valid_image_file(file_path: Path) -> bool:
    """Verifica si un archivo es una imagen válida."""
    # Verificar extensión
    if file_path.suffix.lower() not in settings.supported_extensions:
        return False
    
    # Verificar que el archivo existe y es legible
    if not file_path.is_file():
        return False
    
    # Verificar que el archivo no está vacío
    try:
        if file_path.stat().st_size == 0:
            return False
    except Exception:
        return False
    
    # Validar apertura de imagen (incluyendo HEIC)
    try:
        if file_path.suffix.lower() in {'.heic', '.heif'}:
            heif_file = pillow_heif.read_heif(str(file_path))
            if not heif_file.data:
                return False
            img = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw"
            )
            img.verify()
        else:
            with Image.open(file_path) as img:
                img.verify()
    except Exception:
        return False
    
    return True

def scan_images_recursively(root_path: str, photo_repo: PhotoRepository, duplicate_repo: DuplicateRepository, batch_size: int = 100) -> Generator[List[Dict], None, None]:
    """
    Escanea recursivamente un directorio y retorna información de imágenes válidas en lotes.
    
    Args:
        root_path: Ruta raíz del directorio a escanear
        photo_repo: Repositorio de fotos para validar duplicados
        duplicate_repo: Repositorio de duplicados para registrar duplicados reales
        batch_size: Tamaño del lote para procesar
        
    Yields:
        Lista de diccionarios con información de imágenes válidas encontradas
    """
    root_path_obj = Path(root_path)
    
    if not root_path_obj.exists():
        print(f"Error: El directorio {root_path} no existe")
        return
    
    if not root_path_obj.is_dir():
        print(f"Error: {root_path} no es un directorio")
        return
    
    print(f"🔍 Escaneando directorio: {root_path}")
    print(f"📦 Tamaño de lote: {batch_size} imágenes")
    
    total_files = 0
    valid_images = 0
    already_processed = 0
    duplicates_found = 0
    errors = 0
    current_batch = []
    
    # Recorrer de forma recursiva
    for file_path in root_path_obj.rglob('*'):
        if not file_path.is_file():
            continue
        
        total_files += 1
        
        # Verificar si es una imagen válida
        if not is_valid_image_file(file_path):
            continue
        
        # Calcular hash del archivo
        file_hash = calculate_file_hash(file_path)
        if not file_hash:
            errors += 1
            continue

        # Calcular phash del archivo
        file_phash = calculate_phash(file_path)
        if not file_phash:
            errors += 1
            continue
        
        # Verificar si ya fue procesado usando el repositorio
        existing_photo = photo_repo.get_by_hash(file_hash)
        current_path = str(file_path.absolute())
        
        if existing_photo:
            # Verificar si es la misma foto (mismo hash y mismo path)
            if str(existing_photo.path) == current_path:
                already_processed += 1
                print(f"⏭️  Ya procesada: {file_path.name}")
                continue
            else:
                # Es un duplicado real (mismo hash, diferente path)
                duplicates_found += 1
                print(f"🔄 Duplicado encontrado: {file_path.name} (mismo hash que {existing_photo.filename})")
                
                # Registrar en la tabla de duplicados
                try:
                    photo_dict = existing_photo.to_dict()
                    duplicate_repo.create_duplicate(
                        photo_id=photo_dict['id'],  # La foto actual será el duplicado
                        duplicate_of_id=photo_dict['id'],  # La existente será la original
                        reason="hash_duplicate"
                    )
                    print(f"📝 Duplicado registrado en base de datos")
                except Exception as e:
                    print(f"Error registrando duplicado: {e}")
                
                continue
        
        # Registrar la imagen usando el repositorio
        try:
            bucket_repo = BucketRepository()
            path_in_bucket = bucket_repo.upload_file(current_path, file_path.suffix.lower())
            # Leer el archivo como bytes para convertirlo a WebP
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            web_memory = to_webp(file_bytes)
            
            # Convertir BytesIO a bytes
            web_memory.seek(0)  # Asegurar que estamos al inicio
            web_bytes = web_memory.read()
            path_in_bucket_webp = bucket_repo.upload_file_memoria(web_bytes, ".webp")
            photo_data = {
                'filename': file_path.name,
                'path': path_in_bucket,
                'web_path': path_in_bucket_webp,
                'hash': file_hash,
                'phash': file_phash
                # 'is_new' no se incluye, así que será True por defecto
            }
            
            new_photo = photo_repo.create(photo_data)
            valid_images += 1
            print(f"✅ Imagen registrada: {file_path.name}")
            
            # Agregar al lote actual
            photo_dict = new_photo.to_dict()
            image_info = {
                'id': photo_dict['id'],  # Incluir el ID de la foto
                'filename': file_path.name,
                'path': current_path,
                'hash': file_hash,
                'phash': file_phash,
                'size': file_path.stat().st_size,
                'extension': file_path.suffix.lower()
            }
            current_batch.append(image_info)
            
            # Si el lote está completo, retornarlo y liberar memoria
            if len(current_batch) >= batch_size:
                print(f"📦 Lote completado: {len(current_batch)} imágenes")
                yield current_batch
                current_batch = []  # Liberar memoria del lote anterior
                
        except Exception as e:
            print(f"Error registrando imagen {file_path}: {e}")
            errors += 1
    
    # Retornar el último lote si no está vacío
    if current_batch:
        print(f"📦 Lote final: {len(current_batch)} imágenes")
        yield current_batch
    
    # Mostrar resumen
    print(f"\n📊 Resumen del escaneo:")
    print(f"   Total de archivos revisados: {total_files}")
    print(f"   Imágenes válidas registradas: {valid_images}")
    print(f"   Ya procesadas (mismo hash y path): {already_processed}")
    print(f"   Duplicados reales encontrados: {duplicates_found}")
    print(f"   Errores encontrados: {errors}")
    print(f"   Lotes procesados: {(valid_images + batch_size - 1) // batch_size}")

def load_images_from_folder(folder_path: str, batch_size: int = 100) -> List[Dict]:
    """
    Carga todas las imágenes válidas de una carpeta en lotes.
    
    Args:
        folder_path: Ruta de la carpeta a escanear
        batch_size: Tamaño del lote para procesar (por defecto 100)
        
    Returns:
        Lista de diccionarios con información de las imágenes encontradas
    """
    # Usar la configuración de conexión existente
    session = SessionLocal()
    photo_repo = PhotoRepository(session)
    duplicate_repo = DuplicateRepository(session)
    
    all_images = []
    batch_count = 0
    
    try:
        print(f"🚀 Iniciando procesamiento por lotes...")
        print(f"📁 Carpeta: {folder_path}")
        print(f"📦 Tamaño de lote: {batch_size}")
        print("-" * 50)
        
        for batch in scan_images_recursively(folder_path, photo_repo, duplicate_repo, batch_size):
            batch_count += 1
            all_images.extend(batch)
            
            print(f"✅ Lote #{batch_count} procesado: {len(batch)} imágenes")
            print(f"📊 Total acumulado: {len(all_images)} imágenes")
            print("-" * 30)
        
        print(f"\n🎉 Proceso completado.")
        print(f"📈 Total de imágenes cargadas: {len(all_images)}")
        print(f"📦 Total de lotes procesados: {batch_count}")
        
    except Exception as e:
        print(f"❌ Error durante el escaneo: {e}")
    
    finally:
        session.close()
    
    return all_images 