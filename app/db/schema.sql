-- Crear base de datos
CREATE DATABASE IF NOT EXISTS photo_organizer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE photo_organizer;

-- Tabla de fotos procesadas
CREATE TABLE photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    path TEXT NOT NULL,
    hash CHAR(64) NOT NULL, -- SHA256
    phash VARCHAR(32), -- Hash perceptual (pHash)
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_new BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE(hash)
);

-- Tabla de personas detectadas
CREATE TABLE people (
    id INT AUTO_INCREMENT PRIMARY KEY,
    label VARCHAR(100) NOT NULL, -- Ej: "Persona 1", "Persona 2"
    avg_embedding TEXT,          -- Vector promedio serializado (JSON)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Relación N:M entre fotos y personas (una foto puede tener muchas personas, y una persona puede aparecer en muchas fotos)
CREATE TABLE photo_people (
    photo_id INT NOT NULL,
    person_id INT NOT NULL,
    PRIMARY KEY (photo_id, person_id),
    FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
);

-- Embeddings individuales por rostro detectado
CREATE TABLE face_embeddings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    photo_id INT NOT NULL,
    embedding TEXT NOT NULL, -- Vector facial como arreglo JSON
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE,
    FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE
);

-- Registro de imágenes duplicadas
CREATE TABLE duplicates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    photo_id INT NOT NULL,
    duplicate_of_id INT NOT NULL,
    reason VARCHAR(100), -- Ej: "hash", "visual_embedding"
    FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
    FOREIGN KEY (duplicate_of_id) REFERENCES photos(id) ON DELETE CASCADE,
    UNIQUE(photo_id, duplicate_of_id)
);
