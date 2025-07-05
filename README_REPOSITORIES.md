# Repositorios - Organizador de Fotos

## 📋 Descripción

Este documento describe los repositorios implementados para el organizador de fotos por reconocimiento facial. Los repositorios proporcionan una capa de abstracción sobre los modelos SQLAlchemy, ofreciendo métodos específicos para cada entidad del dominio.

## 🏗️ Arquitectura de Repositorios

### 📊 Diagrama de Repositorios

```
┌─────────────────┐
│ BaseRepository  │ ← Clase base genérica
└─────────────────┘
         │
         ├─── PhotoRepository
         ├─── PersonRepository  
         ├─── FaceEmbeddingRepository
         ├─── PhotoPeopleRepository
         └─── DuplicateRepository
```

## 🗂️ Repositorios Implementados

### 1. **BaseRepository** - Repositorio Base

**Propósito:** Clase base genérica que proporciona operaciones CRUD básicas.

**Métodos Base:**
- `get(id)`: Obtiene entidad por ID
- `list_all()`: Lista todas las entidades
- `create(obj_in)`: Crea nueva entidad
- `delete(id)`: Elimina entidad por ID

**Uso:**
```python
from db.repositories import BaseRepository
from db.models import Photo

class PhotoRepository(BaseRepository[Photo]):
    def __init__(self, session):
        super().__init__(Photo, session)
```

### 2. **PhotoRepository** - Repositorio de Fotos

**Propósito:** Maneja operaciones específicas para entidades Photo.

**Métodos Específicos:**
- `get_by_hash(hash_value)`: Obtiene foto por hash SHA256

**Uso:**
```python
from db.repositories import PhotoRepository

photo_repo = PhotoRepository(session)

# Crear foto
photo_data = {
    'filename': 'foto.jpg',
    'path': '/path/to/foto.jpg',
    'hash': 'abc123hash'
}
photo = photo_repo.create(photo_data)

# Buscar por hash
found_photo = photo_repo.get_by_hash('abc123hash')
```

### 3. **PersonRepository** - Repositorio de Personas

**Propósito:** Maneja operaciones específicas para entidades Person.

**Métodos Específicos:**
- `get_by_label(label)`: Obtiene persona por etiqueta
- `get_photos_count(person_id)`: Conteo de fotos por persona
- `get_people_with_photo_count()`: Personas con conteo de fotos
- `get_people_by_photo(photo_id)`: Personas en una foto
- `get_embeddings(person_id)`: Embeddings de una persona
- `update_avg_embedding(person_id, embedding)`: Actualiza embedding promedio
- `get_people_with_embeddings()`: Personas con embeddings
- `get_next_label()`: Genera siguiente etiqueta disponible

**Uso:**
```python
from db.repositories import PersonRepository

person_repo = PersonRepository(session)

# Crear persona
person_data = {
    'label': 'Persona 1',
    'avg_embedding': json.dumps([0.1, 0.2, 0.3])
}
person = person_repo.create(person_data)

# Obtener por etiqueta
found_person = person_repo.get_by_label('Persona 1')

# Obtener conteo de fotos
photos_count = person_repo.get_photos_count(person.id)

# Generar siguiente etiqueta
next_label = person_repo.get_next_label()  # "Persona 2"
```

### 4. **FaceEmbeddingRepository** - Repositorio de Embeddings

**Propósito:** Maneja operaciones específicas para embeddings faciales.

**Métodos Específicos:**
- `get_by_person(person_id)`: Embeddings de una persona
- `get_by_photo(photo_id)`: Embeddings de una foto
- `get_by_person_and_photo(person_id, photo_id)`: Embeddings específicos
- `get_embeddings_arrays(person_id)`: Embeddings como arrays
- `create_with_array(person_id, photo_id, embedding_array)`: Crear desde array
- `get_average_embedding(person_id)`: Calcula embedding promedio
- `get_embeddings_count(person_id)`: Conteo de embeddings
- `delete_by_person(person_id)`: Eliminar embeddings de persona
- `delete_by_photo(photo_id)`: Eliminar embeddings de foto
- `find_similar_embeddings(target, threshold)`: Encuentra embeddings similares

**Uso:**
```python
from db.repositories import FaceEmbeddingRepository

embedding_repo = FaceEmbeddingRepository(session)

# Crear embedding desde array
embedding = embedding_repo.create_with_array(
    person_id=1, 
    photo_id=1, 
    embedding_array=[0.1, 0.2, 0.3, 0.4, 0.5]
)

# Obtener embeddings de una persona
embeddings = embedding_repo.get_by_person(person_id=1)

# Calcular embedding promedio
avg_embedding = embedding_repo.get_average_embedding(person_id=1)

# Encontrar embeddings similares
similar = embedding_repo.find_similar_embeddings(
    target=[0.1, 0.2, 0.3, 0.4, 0.5], 
    threshold=0.6
)
```

### 5. **PhotoPeopleRepository** - Repositorio de Relaciones

**Propósito:** Maneja relaciones N:M entre fotos y personas.

**Métodos Específicos:**
- `get_by_photo(photo_id)`: Relaciones de una foto
- `get_by_person(person_id)`: Relaciones de una persona
- `get_people_by_photo(photo_id)`: Personas en una foto
- `get_photos_by_person(person_id)`: Fotos de una persona
- `create_relationship(photo_id, person_id)`: Crear relación
- `delete_relationship(photo_id, person_id)`: Eliminar relación
- `delete_by_photo(photo_id)`: Eliminar todas las relaciones de una foto
- `delete_by_person(person_id)`: Eliminar todas las relaciones de una persona
- `get_people_count_by_photo(photo_id)`: Conteo de personas por foto
- `get_photos_count_by_person(person_id)`: Conteo de fotos por persona
- `exists_relationship(photo_id, person_id)`: Verificar si existe relación

**Uso:**
```python
from db.repositories import PhotoPeopleRepository

photo_people_repo = PhotoPeopleRepository(session)

# Crear relación
photo_people_repo.create_relationship(photo_id=1, person_id=1)

# Obtener personas en una foto
people = photo_people_repo.get_people_by_photo(photo_id=1)

# Obtener fotos de una persona
photos = photo_people_repo.get_photos_by_person(person_id=1)

# Verificar si existe relación
exists = photo_people_repo.exists_relationship(photo_id=1, person_id=1)
```

### 6. **DuplicateRepository** - Repositorio de Duplicados

**Propósito:** Maneja registros de imágenes duplicadas.

**Métodos Específicos:**
- `get_by_photo(photo_id)`: Duplicados de una foto
- `get_by_original(original_photo_id)`: Duplicados de una foto original
- `get_duplicates_by_reason(reason)`: Duplicados por razón
- `create_duplicate(photo_id, duplicate_of_id, reason)`: Crear duplicado
- `delete_by_photo(photo_id)`: Eliminar duplicados de una foto
- `delete_by_original(original_photo_id)`: Eliminar duplicados de una original
- `get_duplicates_count(photo_id)`: Conteo de duplicados
- `get_duplicates_summary()`: Resumen de duplicados por razón
- `exists_duplicate(photo_id, duplicate_of_id)`: Verificar si existe duplicado
- `get_duplicate_chains()`: Obtener cadenas de duplicados
- `get_duplicate_groups()`: Agrupar duplicados por original

**Uso:**
```python
from db.repositories import DuplicateRepository

duplicate_repo = DuplicateRepository(session)

# Crear duplicado
duplicate = duplicate_repo.create_duplicate(
    photo_id=3, 
    duplicate_of_id=1, 
    reason="hash"
)

# Obtener duplicados de una foto
duplicates = duplicate_repo.get_by_photo(photo_id=3)

# Obtener resumen de duplicados
summary = duplicate_repo.get_duplicates_summary()

# Obtener grupos de duplicados
groups = duplicate_repo.get_duplicate_groups()
```

## 🚀 Uso Completo

### Configuración Inicial

```python
from sqlalchemy import create_engine
from db.models import create_tables, get_session
from db.repositories import (
    PhotoRepository, PersonRepository, FaceEmbeddingRepository,
    PhotoPeopleRepository, DuplicateRepository
)

# Configurar base de datos
engine = create_engine('sqlite:///photos.db')
create_tables(engine)
session = get_session(engine)

# Crear repositorios
photo_repo = PhotoRepository(session)
person_repo = PersonRepository(session)
embedding_repo = FaceEmbeddingRepository(session)
photo_people_repo = PhotoPeopleRepository(session)
duplicate_repo = DuplicateRepository(session)
```

### Flujo de Trabajo Típico

```python
# 1. Crear foto
photo = photo_repo.create({
    'filename': 'foto.jpg',
    'path': '/path/to/foto.jpg',
    'hash': 'abc123hash'
})

# 2. Crear persona
person = person_repo.create({
    'label': 'Persona 1',
    'avg_embedding': json.dumps([0.1, 0.2, 0.3])
})

# 3. Crear relación
photo_people_repo.create_relationship(photo.id, person.id)

# 4. Crear embedding
embedding = embedding_repo.create_with_array(
    person.id, photo.id, [0.1, 0.2, 0.3, 0.4, 0.5]
)

# 5. Si es duplicado
duplicate_repo.create_duplicate(photo.id, original_photo.id, "hash")
```

## 📊 Consultas Avanzadas

### Estadísticas Complejas

```python
# Obtener todas las personas con conteo de fotos
people_with_counts = photo_people_repo.get_people_with_photos_count()

# Obtener todas las fotos con conteo de personas
photos_with_counts = photo_people_repo.get_photos_with_people_count()

# Obtener resumen de duplicados
duplicates_summary = duplicate_repo.get_duplicates_summary()

# Obtener fotos con duplicados
photos_with_duplicates = duplicate_repo.get_photos_with_duplicates_count()
```

### Análisis de Embeddings

```python
# Calcular embedding promedio de una persona
avg_embedding = embedding_repo.get_average_embedding(person_id=1)

# Encontrar embeddings similares
similar_embeddings = embedding_repo.find_similar_embeddings(
    target=[0.1, 0.2, 0.3, 0.4, 0.5],
    threshold=0.6
)

# Obtener embeddings con información de persona
embeddings_with_info = embedding_repo.get_embeddings_with_person_info(photo_id=1)
```

### Gestión de Duplicados

```python
# Obtener cadenas de duplicados
chains = duplicate_repo.get_duplicate_chains()

# Obtener grupos de duplicados
groups = duplicate_repo.get_duplicate_groups()

# Verificar si existe duplicado
exists = duplicate_repo.exists_duplicate(photo_id=3, duplicate_of_id=1)
```

## 🔧 Patrones de Diseño

### Repository Pattern

Los repositorios implementan el patrón Repository, que:

- **Abstrae la persistencia**: Oculta detalles de la base de datos
- **Centraliza la lógica de acceso**: Todas las consultas están en un lugar
- **Facilita testing**: Permite mockear repositorios para pruebas
- **Mejora mantenibilidad**: Cambios en la base de datos solo afectan repositorios

### Generic Repository

El `BaseRepository` proporciona operaciones CRUD genéricas:

```python
class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session
    
    def get(self, id: int) -> Optional[T]:
        return self.session.get(self.model, id)
    
    def list_all(self) -> List[T]:
        return self.session.query(self.model).all()
    
    def create(self, obj_in: dict) -> T:
        obj = self.model(**obj_in)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj
```

## 🧪 Testing

### Ejecutar Ejemplo

```bash
python example_repositories.py
```

### Pruebas Unitarias

```python
import unittest
from sqlalchemy import create_engine
from db.models import create_tables, get_session
from db.repositories import PhotoRepository

class TestPhotoRepository(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        create_tables(self.engine)
        self.session = get_session(self.engine)
        self.repo = PhotoRepository(self.session)
    
    def test_create_photo(self):
        photo_data = {
            'filename': 'test.jpg',
            'path': '/path/test.jpg',
            'hash': 'testhash'
        }
        photo = self.repo.create(photo_data)
        self.assertIsNotNone(photo.id)
        self.assertEqual(photo.filename, 'test.jpg')
    
    def test_get_by_hash(self):
        # Crear foto
        photo_data = {'filename': 'test.jpg', 'path': '/path/test.jpg', 'hash': 'testhash'}
        self.repo.create(photo_data)
        
        # Buscar por hash
        found = self.repo.get_by_hash('testhash')
        self.assertIsNotNone(found)
        self.assertEqual(found.filename, 'test.jpg')
    
    def tearDown(self):
        self.session.close()
```

## 📝 Notas de Desarrollo

### Gestión de Sesiones

- **Siempre cerrar sesiones**: Usar `finally` para cerrar sesiones
- **Manejo de transacciones**: Usar `commit()` y `rollback()` apropiadamente
- **Context managers**: Considerar usar context managers para sesiones

### Optimización de Consultas

- **Eager loading**: Usar `joinedload()` para cargar relaciones
- **Lazy loading**: Evitar N+1 queries
- **Batch operations**: Usar `bulk_insert_mappings()` para inserciones masivas

### Manejo de Errores

```python
try:
    photo = photo_repo.create(photo_data)
    session.commit()
except Exception as e:
    session.rollback()
    logger.error(f"Error creating photo: {e}")
    raise
```

## 🔄 Próximos Pasos

- **Implementar cache**: Cache para consultas frecuentes
- **Agregar índices**: Índices para optimizar consultas
- **Implementar paginación**: Paginación para listas grandes
- **Agregar validaciones**: Validaciones de datos en repositorios
- **Implementar eventos**: Eventos para operaciones importantes
- **Agregar logging**: Logging detallado de operaciones 