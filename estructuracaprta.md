```mermaid
sequenceDiagram
    participant CLI as "CLI o endpoint"
    participant PR as "Photo Reader"
    participant DB as "DB"
    participant B as "Bucket"
    participant DBV as "DBV"

    CLI->>PR: Envía foto
    PR->>PR: Obtiene hash
    PR->>DB: Consulta foto por hash
    DB-->>PR: Devuelve foto
    PR->>PR: Valida si la foto existe
    PR-->>CLI: Si existe devuelve "foto existente"
    PR->>B: Guarda la foto
    PR->>DB: Guarda información de la foto
    DB-->>PR: Devuelve foto entity
    PR->>PR: Obtiene embeddings
    PR->>DBV: Consulta similitud
    DBV-->>PR: Devuelve fotos por similitud
    PR->>DB: Guarda fotos repetidas
    PR->>DBV: Guarda embeddings de foto
    PR->>PR: Obtiene personas
    PR->>DBV: Consulta persona por similitud
    DBV-->>PR: Retorna persona por similitud
    PR->>DB: Crea persona si no existe
    DB-->>PR: Retorna persona creada
    PR->>DB: Relaciona Persona a foto
    PR->>DBV: Crea persona si no existe
    PR-->>CLI: Retorna imagen guardada correctamente


```

```text
home-photo-cli/
│── pyproject.toml                                # Dependencias
│── README.md
│── src/
│   ├── app/
│   │   ├── config/
│   │   │   ├── settings.py                       # Configuración de env, paths, etc.
│   │   │   └── container.py                      # IoC container / Dependency Injection
│   │   │  
│   │   ├── domain/                               # Núcleo del negocio (reglas de dominio)
│   │   │   ├── models/                           # Entidades, Value Objects
│   │   │   │   └──entities.py                    # entities
│   │   │   │
│   │   │   ├── repositories/                     # Interfaces (puertos de salida)
│   │   │   │   ├──base_repository.py             # interfaz base para repositorios
│   │   │   │   ├──photo_repository.py            # interfaz para repositorio de fotos
│   │   │   │   ├──person_repository.py           # interfaz para repositorio de personas
│   │   │   │   ├──duplicate_repository.py        # interfaz para repositorio de duplicados
│   │   │   │   ├──photo_people_repository.py     # interfaz para repositorio photo_people
│   │   │   │   └──photo_tag_repository.py        # interfaz para repositorio photo_tag
│   │   │   └── interfaces/                       # Interfaces de servicios
│   │   │       ├──hashing_service.py             # interfaz para servicio de hashing
│   │   │       ├──embedding_service.py           # interfaz para servicio de embeddings
│   │   │       ├──face_recognition_service.py    # interfaz para servicio de reconocimiento facial
│   │   │       ├──vector_repository.py           # interfaz para repositorio de vector db
│   │   │       └──photo_storage_service.py       # interfaz para servicio de storage de fotos
│   │   │
│   │   ├── application/                          # Orquesta casos de uso
│   │   │   └── use_cases/                        # Lógica de aplicación
│   │   │       └──process_photo.py               # procesa la foto
│   │   │
│   │   ├── infrastructure/                       # Adaptadores concretos
│   │   │   ├── db/                               # Implementaciones de repositorios (ej. SQLAlchemy)
│   │   │   │   ├──models.py                      # Modelos de SQLAlchemy
│   │   │   │   └──repositories/                  # Repositorios para comunicarse con la base de datos
│   │   │   │      ├──base_repository.py          # repositorio base para loa metos en comun (get_by_id, get_all, create, delete, update)
│   │   │   │      ├──photo_repository.py         # repositorio para el modelo photo
│   │   │   │      ├──person_repository.py        # repositorio para el modelo person
│   │   │   │      ├──duplicate_repository.py     # repositorio para el modelo fotos duplicadas
│   │   │   │      ├──photo_people_repository.py  # repositorio para el modelo photo_people
│   │   │   │      └──photo_tag_repository.py     # repositorio para el modelo photos tags
│   │   │   │      
│   │   │   ├── services/                         # implementacion de servicios
│   │   │   │   ├──hashing_service.py             # servicio para hashing
│   │   │   │   ├──embedding_service.py           # servicio para obtener los embeddings
│   │   │   │   └──face_recognition_service.py     # servicio para opbtener las personas de la foto
│   │   │   │
│   │   │   ├── vector_db/                        # implementacion de los repositorios de vector db
│   │   │   │   └──vector_repository.py           # repositorio para vector db
│   │   │   │
│   │   │   ├── storage/                          # implementacion del storage
│   │   │   │   └──photo_storage_service.py       # servicio de storage para guardar las fotos
│   │   │   │
│   │   │   ├── api/                              # Adaptador de entrada: FastAPI
│   │   │   └── cli/                              # Adaptador de entrada: CLI (Typer/Click)
│   │   │
│   │   └── config/                               # Configuración (env, settings)
│   │
│   └── main_api.py                               # Punto de entrada para FastAPI
│   └── main_cli.py                               # Punto de entrada para CLI
│
└── tests/
    ├── unit/                                     # Pruebas unitarias de dominio
    ├── integration/                              # Pruebas de adaptadores (db, api, cli)
    └── e2e/                                      # Flujo completo
```