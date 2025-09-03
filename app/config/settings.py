# Configuraciones generales (rutas, DB, lote, etc.)

SETTINGS = {
    "db_url": "mysql://user:password@localhost/dbname",
    "image_folder": "./images",
    "batch_size": 32
}

# Extensiones de imagen soportadas para la tarea IMG-01
SUPPORTED_IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.heic', '.heif'
} 