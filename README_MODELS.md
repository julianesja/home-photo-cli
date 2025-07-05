# Modelos SQLAlchemy - Organizador de Fotos

## 📋 Descripción

Este documento describe los modelos SQLAlchemy implementados para el organizador de fotos por reconocimiento facial. Los modelos están basados en el esquema SQL definido en `schema.sql` y proporcionan una interfaz orientada a objetos para trabajar con la base de datos.

## 🏗️ Arquitectura de Modelos

### 📊 Diagrama de Relaciones

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│    Photo    │    │ PhotoPeople  │    │   Person    │
├─────────────┤    ├──────────────┤    ├─────────────┤
│ id (PK)     │◄───┤ photo_id (FK)│    │ id (PK)     │
│ filename    │    │ person_id(FK)│───►│ label       │
│ path        │    └──────────────┘    │ avg_embedding│
│ hash        │                        │ created_at  │
│ processed_at│                        └─────────────┘
└─────────────┘                                │
       │                                       │
       │                                       │
       ▼                                       ▼
┌─────────────┐                        ┌─────────────┐
│ FaceEmbedding│                        │  Duplicate  │
├─────────────┤                        ├─────────────┤
│ id (PK)     │                        │ id (PK)     │
│ person_id(FK)│                        │ photo_id(FK)│
│ photo_id(FK)│                        │ duplicate_of_id(FK)│
│ embedding   │                        │ reason      │
└─────────────┘                        └─────────────┘
```

## 🗂️ Modelos Implementados

### 1. **Photo** - Fotos Procesadas

**Tabla:** `photos`

**Propósito:** Almacena información de las fotos procesadas en el sistema.

**Campos:**
- `id` (Integer, PK): Identificador único
- `filename` (String(255)): Nombre del archivo
- `path` (Text): Ruta completa del archivo
- `hash` (String(64), Unique): Hash SHA256 del archivo
- `processed_at` (DateTime): Timestamp de procesamiento

**Relaciones:**
- `people`: Relación N:M con Person a través de PhotoPeople
- `face_embeddings`: Relación 1:N con FaceEmbedding
- `duplicates_as_original`: Relación 1:N con Duplicate (como original)
- `duplicates_as_duplicate`: Relación 1:N con Duplicate (como duplicado)

**Métodos:**
- `to_dict()`: Convierte el modelo a diccionario
- `__repr__()`: Representación string del modelo

### 2. **Person** - Personas Detectadas

**Tabla:** `people`

**Propósito:** Representa las personas detectadas en las fotos.

**Campos:**
- `id` (Integer, PK): Identificador único
- `label` (String(100)): Etiqueta de la persona (ej: "Persona 1")
- `avg_embedding` (Text): Vector promedio serializado en JSON
- `created_at` (DateTime): Timestamp de creación

**Relaciones:**
- `photos`: Relación N:M con Photo a través de PhotoPeople
- `face_embeddings`: Relación 1:N con FaceEmbedding

**Métodos:**
- `to_dict()`: Convierte el modelo a diccionario
- `get_avg_embedding_array()`: Obtiene embedding como lista de floats
- `set_avg_embedding_array()`: Establece embedding desde lista de floats
- `__repr__()`: Representación string del modelo

### 3. **PhotoPeople** - Relación N:M

**Tabla:** `photo_people`

**Propósito:** Tabla de relación N:M entre fotos y personas.

**Campos:**
- `photo_id` (Integer, FK): Referencia a Photo
- `person_id` (Integer, FK): Referencia a Person

**Relaciones:**
- `photo`: Relación con Photo
- `person`: Relación con Person

### 4. **FaceEmbedding** - Embeddings Faciales

**Tabla:** `face_embeddings`

**Propósito:** Almacena embeddings individuales por rostro detectado.

**Campos:**
- `id` (Integer, PK): Identificador único
- `person_id` (Integer, FK): Referencia a Person
- `photo_id` (Integer, FK): Referencia a Photo
- `embedding` (Text): Vector facial serializado en JSON

**Relaciones:**
- `person`: Relación con Person
- `photo`: Relación con Photo

**Métodos:**
- `get_embedding_array()`: Obtiene embedding como lista de floats
- `set_embedding_array()`: Establece embedding desde lista de floats
- `to_dict()`: Convierte el modelo a diccionario
- `__repr__()`: Representación string del modelo

### 5. **Duplicate** - Registro de Duplicados

**Tabla:** `duplicates`

**Propósito:** Registra imágenes duplicadas.

**Campos:**
- `id` (Integer, PK): Identificador único
- `photo_id` (Integer, FK): Referencia a foto duplicada
- `duplicate_of_id` (Integer, FK): Referencia a foto original
- `reason` (String(100)): Razón de la duplicación

**Relaciones:**
- `original_photo`: Relación con Photo (como original)
- `duplicate_photo`: Relación con Photo (como duplicado)

**Constraints:**
- Unique constraint en (photo_id, duplicate_of_id)

**Métodos:**
- `to_dict()`: Convierte el modelo a diccionario
- `__repr__()`: Representación string del modelo

## 🛠️ Funciones de Utilidad

### Gestión de Base de Datos

```python
from db.models import create_tables, drop_tables, get_session

# Crear todas las tablas
create_tables(engine)

# Eliminar todas las tablas
drop_tables(engine)

# Obtener sesión
session = get_session(engine)
```

### Funciones de Inserción

```python
from db.models import (
    insert_photo, insert_person, insert_face_embedding, insert_duplicate
)

# Insertar foto
photo = insert_photo(session, "foto.jpg", "/path/to/foto.jpg", "hash123")

# Insertar persona
person = insert_person(session, "Persona 1", [0.1, 0.2, 0.3])

# Insertar embedding facial
embedding = insert_face_embedding(session, person.id, photo.id, [0.1, 0.2, 0.3])

# Insertar duplicado
duplicate = insert_duplicate(session, photo.id, original_photo.id, "hash")
```

### Funciones de Consulta

```python
from db.models import (
    query_photos_by_person, query_person_by_photo, 
    query_photo_by_hash, query_duplicates
)

# Consultar fotos por persona
photos = query_photos_by_person(session, person_id)

# Consultar personas por foto
people = query_person_by_photo(session, photo_id)

# Consultar foto por hash
photo = query_photo_by_hash(session, "hash123")

# Consultar duplicados
duplicates = query_duplicates(session, photo_id)
```

## 💾 Configuración de Base de Datos

### SQLite (Desarrollo)

```python
from sqlalchemy import create_engine

# Base de datos en memoria
engine = create_engine('sqlite:///:memory:')

# Base de datos en archivo
engine = create_engine('sqlite:///photos.db')
```

### MySQL (Producción)

```python
from sqlalchemy import create_engine

# Conexión MySQL
engine = create_engine(
    'mysql+mysqlconnector://user:password@localhost/photo_organizer'
)
```

## 🔄 Ejemplo de Uso Completo

```python
from sqlalchemy import create_engine
from db.models import (
    create_tables, get_session, Photo, Person, PhotoPeople,
    insert_photo, insert_person
)

# Configurar base de datos
engine = create_engine('sqlite:///photos.db')
create_tables(engine)
session = get_session(engine)

try:
    # Insertar datos
    photo = insert_photo(session, "foto1.jpg", "/path/to/foto1.jpg", "hash123")
    person = insert_person(session, "Persona 1", [0.1, 0.2, 0.3])
    
    # Crear relación
    photo_person = PhotoPeople(photo_id=photo.id, person_id=person.id)
    session.add(photo_person)
    session.commit()
    
    print("✅ Datos insertados exitosamente")
    
except Exception as e:
    session.rollback()
    print(f"❌ Error: {e}")
    
finally:
    session.close()
```

## 📊 Consultas Avanzadas

### Obtener Todas las Fotos con Personas

```python
from sqlalchemy.orm import joinedload

photos_with_people = session.query(Photo).options(
    joinedload(Photo.people).joinedload(PhotoPeople.person)
).all()

for photo in photos_with_people:
    print(f"Foto: {photo.filename}")
    for photo_person in photo.people:
        print(f"  - {photo_person.person.label}")
```

### Obtener Estadísticas

```python
from sqlalchemy import func

# Total de fotos
total_photos = session.query(func.count(Photo.id)).scalar()

# Total de personas
total_people = session.query(func.count(Person.id)).scalar()

# Fotos por persona
photos_per_person = session.query(
    Person.label,
    func.count(PhotoPeople.photo_id).label('photo_count')
).join(PhotoPeople).group_by(Person.id).all()
```

## 🔧 Migraciones

Para cambios en el esquema, se recomienda usar Alembic:

```bash
# Instalar Alembic
pip install alembic

# Inicializar
alembic init alembic

# Crear migración
alembic revision --autogenerate -m "Add new column"

# Aplicar migración
alembic upgrade head
```

## 🧪 Testing

### Ejecutar Ejemplo

```bash
python example_models.py
```

### Pruebas Unitarias

```python
import unittest
from sqlalchemy import create_engine
from db.models import create_tables, Photo, Person

class TestModels(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        create_tables(self.engine)
        self.session = get_session(self.engine)
    
    def test_insert_photo(self):
        photo = insert_photo(self.session, "test.jpg", "/path/test.jpg", "hash")
        self.assertIsNotNone(photo.id)
        self.assertEqual(photo.filename, "test.jpg")
    
    def tearDown(self):
        self.session.close()
```

## 📝 Notas de Desarrollo

- **Serialización JSON**: Los embeddings se almacenan como JSON strings para compatibilidad
- **Cascade Delete**: Las relaciones están configuradas para eliminar en cascada
- **Type Safety**: Se usan type hints para mejor documentación
- **Session Management**: Siempre cerrar sesiones para evitar memory leaks
- **Error Handling**: Manejar excepciones y hacer rollback en caso de error

## 🔄 Próximos Pasos

- Implementar índices para optimizar consultas
- Agregar validaciones de datos
- Implementar cache para consultas frecuentes
- Agregar logging para operaciones de base de datos
- Implementar backup automático 