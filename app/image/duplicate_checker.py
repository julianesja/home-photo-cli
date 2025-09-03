from app.db.connection import SessionLocal
from app.db.repositories import PhotoRepository, DuplicateRepository
from app.db.models import Photo
import imagehash

def hamming_distance(phash1: str, phash2: str) -> int:
    """Calcula la distancia de Hamming entre dos phash en formato string."""
    return imagehash.hex_to_hash(str(phash1)) - imagehash.hex_to_hash(str(phash2))

def check_new_photos_for_duplicates(threshold: int = 5):
    """
    Valida todas las fotos nuevas (is_new=True) contra todas las fotos existentes usando phash.
    Registra duplicados en la tabla duplicates si la distancia de Hamming <= threshold.
    Cambia is_new a False después de validar cada foto nueva.
    """
    session = SessionLocal()
    photo_repo = PhotoRepository(session)
    duplicate_repo = DuplicateRepository(session)

    # Obtener todas las fotos nuevas (instancias reales)
    new_photos = photo_repo.get_new_photos()
    if not new_photos:
        print("No hay fotos nuevas para validar.")
        session.close()
        return

    # Obtener todas las fotos existentes (instancias reales)
    all_photos = photo_repo.all()
    print(f"Validando {len(new_photos)} fotos nuevas contra {len(all_photos)} fotos en total...")

    for new_photo in new_photos:
        phash_new = getattr(new_photo, 'phash', None)
        id_new = getattr(new_photo, 'id', None)
        if not phash_new or id_new is None:
            print(f"Foto nueva id={id_new} no tiene phash o id, se omite.")
            setattr(new_photo, 'is_new', False)
            session.commit()
            continue
        for existing_photo in all_photos:
            phash_exist = getattr(existing_photo, 'phash', None)
            id_exist = getattr(existing_photo, 'id', None)
            if id_new == id_exist or id_exist is None:
                continue  # No comparar consigo misma o sin id
            if not phash_exist:
                continue  # No comparar si la otra no tiene phash
            dist = hamming_distance(phash_new, phash_exist)
            if dist <= threshold:
                # Verificar si ya existe el registro de duplicado
                if not duplicate_repo.exists_duplicate(int(id_new), int(id_exist)):
                    duplicate_repo.create_duplicate(
                        photo_id=int(id_new),
                        duplicate_of_id=int(id_exist),
                        reason=f"phash_{dist}"
                    )
                    print(f"Duplicado registrado: nueva={id_new} duplicado_de={id_exist} dist={dist}")
        # Marcar la foto como ya validada
        setattr(new_photo, 'is_new', False)
        session.commit()
        print(f"Foto id={id_new} marcada como validada (is_new=False)")
    session.close()
