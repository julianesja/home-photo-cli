# Validaciones de tipo de imagen, extensiones, etc.
from io import BytesIO
from PIL import Image
import pillow_heif

def to_webp(file_bytes: bytes, quality: int = 90) -> BytesIO:
    """
    Convierte una imagen en cualquier formato soportado a WebP en memoria.
    Maneja archivos HEIC/HEIF usando pillow-heif.
    
    :param file_bytes: Bytes de la imagen original.
    :param quality: Calidad de salida (0-100).
    :return: BytesIO con la imagen en formato WebP.
    """
    try:
        # Verificar si es un archivo HEIC/HEIF por los primeros bytes
        if file_bytes.startswith(b'\x00\x00\x00') and b'ftypheic' in file_bytes[:20]:
            # Es un archivo HEIC/HEIF
            heif_file = pillow_heif.read_heif(file_bytes)
            if not heif_file.data:
                raise ValueError("HEIF file no tiene datos de imagen válidos")
            
            img = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw"
            )
        else:
            # Es un formato estándar (JPEG, PNG, etc.)
            img = Image.open(BytesIO(file_bytes))
        
        # Normalizamos a RGB si la imagen tiene transparencia o paleta
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        output = BytesIO()
        img.save(output, format="WEBP", quality=quality)
        output.seek(0)
        return output
        
    except Exception as e:
        print(f"❌ Error en to_webp: {type(e).__name__}: {e}")
        print(f"   Tamaño de bytes recibidos: {len(file_bytes)} bytes")
        print(f"   Primeros 20 bytes: {file_bytes[:20] if len(file_bytes) >= 20 else file_bytes}")
        raise e