"""
Clustering de rostros similares usando DBSCAN.
Implementa la tarea FACE-02: Agrupar rostros similares con clustering no supervisado
"""

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import euclidean_distances
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
import logging

from app.db.repositories import PersonRepository, FaceEmbeddingRepository, PhotoPeopleRepository
from app.db.connection import SessionLocal
from app.face.detector import detect_faces_and_embeddings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceClusterer:
    """
    Clase para agrupar rostros similares usando clustering no supervisado.
    """
    
    def __init__(self, eps: float = 0.6, min_samples: int = 2):
        """
        Inicializa el clusterer de rostros.
        
        Args:
            eps: Distancia máxima entre puntos para ser considerados vecinos
            min_samples: Número mínimo de muestras para formar un cluster
        """
        self.eps = eps
        self.min_samples = min_samples
        self.dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')
        
    def cluster_faces(self, embeddings: List[List[float]]) -> Tuple[np.ndarray, List[int]]:
        """
        Agrupa embeddings de rostros usando DBSCAN.
        
        Args:
            embeddings: Lista de embeddings faciales
            
        Returns:
            Tuple con (labels, cluster_ids)
        """
        if not embeddings:
            logger.warning("No hay embeddings para clusterizar")
            return np.array([]), []
        
        # Convertir a numpy array
        embeddings_array = np.array(embeddings)
        logger.info(f"Aplicando DBSCAN a {len(embeddings)} embeddings con eps={self.eps}, min_samples={self.min_samples}")
        
        # Aplicar DBSCAN
        labels = self.dbscan.fit_predict(embeddings_array)
        
        # Obtener IDs únicos de clusters (excluyendo -1 que son outliers)
        cluster_ids = list(set(labels)) 
        if -1 in cluster_ids:
            cluster_ids.remove(-1)  # Remover outliers
            
        logger.info(f"DBSCAN completado. Labels: {labels}, Clusters encontrados: {len(cluster_ids)}")
        return labels, cluster_ids
    
    def calculate_cluster_centroid(self, embeddings: List[List[float]]) -> List[float]:
        """
        Calcula el centroide (embedding promedio) de un cluster.
        
        Args:
            embeddings: Lista de embeddings del cluster
            
        Returns:
            Embedding promedio del cluster
        """
        if not embeddings:
            return []
        
        embeddings_array = np.array(embeddings)
        centroid = np.mean(embeddings_array, axis=0)
        return centroid.tolist()
    
    def find_similar_person(self, avg_embedding: List[float], person_repo: PersonRepository, 
                          threshold: float = 0.6) -> Optional[int]:
        """
        Busca una persona existente con embedding similar.
        
        Args:
            avg_embedding: Embedding promedio del cluster
            person_repo: Repositorio de personas
            threshold: Umbral de similitud
            
        Returns:
            ID de la persona similar o None si no se encuentra
        """
        people_with_embeddings = person_repo.get_people_with_embeddings()
        
        if not people_with_embeddings:
            logger.info("No hay personas existentes con embeddings para comparar")
            return None
        
        avg_embedding_array = np.array(avg_embedding)
        logger.info(f"Buscando persona similar entre {len(people_with_embeddings)} personas existentes")
        
        for person in people_with_embeddings:
            person_avg = person.get_avg_embedding_array()
            if person_avg:
                distance = np.linalg.norm(avg_embedding_array - np.array(person_avg))
                logger.debug(f"Distancia con persona {person.id}: {distance}")
                if distance <= threshold:
                    person_dict = person.to_dict()
                    logger.info(f"Persona similar encontrada: ID {person_dict['id']} (distancia: {distance})")
                    return person_dict['id']
        
        logger.info("No se encontró persona similar")
        return None

def process_faces_in_batch(photos_batch: List[Dict], batch_size: int = 100) -> Dict:
    """
    Procesa rostros en un lote de fotos usando clustering.
    
    Args:
        photos_batch: Lote de fotos con información
        batch_size: Tamaño del lote para procesamiento
        
    Returns:
        Diccionario con estadísticas del procesamiento
    """
    session = SessionLocal()
    person_repo = PersonRepository(session)
    face_embedding_repo = FaceEmbeddingRepository(session)
    photo_people_repo = PhotoPeopleRepository(session)
    
    clusterer = FaceClusterer(eps=0.6, min_samples=2)
    
    stats = {
        'photos_processed': 0,
        'faces_detected': 0,
        'clusters_created': 0,
        'people_created': 0,
        'people_matched': 0,
        'embeddings_saved': 0,
        'errors': 0
    }
    
    try:
        logger.info(f"Procesando lote de {len(photos_batch)} fotos...")
        
        # Recolectar todos los embeddings del lote
        all_embeddings = []
        embedding_to_photo_map = []  # Mapeo de embedding a información de foto
        
        for photo_info in photos_batch:
            try:
                logger.info(f"Procesando foto: {photo_info.get('filename', 'N/A')}")
                logger.info(f"Foto info: {photo_info}")
                
                # Verificar que la foto tenga ID
                if 'id' not in photo_info:
                    logger.error(f"Foto sin ID: {photo_info.get('filename', 'N/A')}")
                    stats['errors'] += 1
                    continue
                
                # Detectar rostros en la foto
                faces = detect_faces_and_embeddings(photo_info['path'])
                
                if not faces:
                    logger.info(f"No se detectaron rostros en: {photo_info.get('filename', 'N/A')}")
                    continue
                
                stats['photos_processed'] += 1
                stats['faces_detected'] += len(faces)
                
                logger.info(f"Detectados {len(faces)} rostros en: {photo_info.get('filename', 'N/A')}")
                
                # Agregar embeddings al lote
                for face in faces:
                    all_embeddings.append(face['embedding'])
                    embedding_to_photo_map.append({
                        'photo_id': photo_info['id'],
                        'photo_path': photo_info['path'],
                        'embedding': face['embedding'],
                        'location': face['location']
                    })
                
                print(f"✅ Foto procesada: {photo_info['filename']} - {len(faces)} rostros")
                
            except Exception as e:
                logger.error(f"Error procesando {photo_info.get('filename', 'N/A')}: {str(e)}", exc_info=True)
                stats['errors'] += 1
                continue
        
        if not all_embeddings:
            logger.warning("No se encontraron rostros en el lote")
            return stats
        
        # Aplicar clustering
        logger.info(f"Aplicando clustering a {len(all_embeddings)} rostros...")
        labels, cluster_ids = clusterer.cluster_faces(all_embeddings)
        
        logger.info(f"Clusters encontrados: {len(cluster_ids)}")
        print(f"📊 Clusters encontrados: {len(cluster_ids)}")
        
        # Procesar cada cluster
        for cluster_id in cluster_ids:
            logger.info(f"Procesando cluster {cluster_id}")
            
            # Obtener embeddings del cluster
            cluster_embeddings = []
            cluster_photo_map = []
            
            for i, label in enumerate(labels):
                if label == cluster_id:
                    cluster_embeddings.append(all_embeddings[i])
                    cluster_photo_map.append(embedding_to_photo_map[i])
            
            logger.info(f"Cluster {cluster_id} tiene {len(cluster_embeddings)} embeddings")
            
            # Calcular embedding promedio del cluster
            avg_embedding = clusterer.calculate_cluster_centroid(cluster_embeddings)
            
            # Buscar persona similar existente
            similar_person_id = clusterer.find_similar_person(avg_embedding, person_repo)
            
            if similar_person_id:
                # Usar persona existente
                person_id = similar_person_id
                stats['people_matched'] += 1
                logger.info(f"Cluster {cluster_id}: Asignado a persona existente (ID: {person_id})")
                print(f"🔄 Cluster {cluster_id}: Asignado a persona existente (ID: {person_id})")
            else:
                # Crear nueva persona
                try:
                    label = person_repo.get_next_label()
                    # Convertir la lista de embedding a JSON antes de guardar
                    import json
                    avg_embedding_json = json.dumps(avg_embedding)
                    person_data = {
                        'label': label,
                        'avg_embedding': avg_embedding_json
                    }
                    logger.info(f"Creando nueva persona con label: {label}")
                    new_person = person_repo.create(person_data)
                    person_dict = new_person.to_dict()
                    person_id = person_dict['id']
                    stats['people_created'] += 1
                    logger.info(f"Cluster {cluster_id}: Nueva persona creada - {label} (ID: {person_id})")
                    print(f"👤 Cluster {cluster_id}: Nueva persona creada - {label} (ID: {person_id})")
                except Exception as e:
                    logger.error(f"Error creando nueva persona: {str(e)}", exc_info=True)
                    stats['errors'] += 1
                    continue
            
            # Guardar embeddings individuales y relaciones
            for photo_map in cluster_photo_map:
                try:
                    logger.info(f"Guardando embedding para foto {photo_map['photo_id']}")
                    
                    # Verificar si el embedding ya existe antes de crearlo
                    if not face_embedding_repo.exists_embedding(person_id, photo_map['photo_id']):
                        # Guardar embedding individual
                        face_embedding_repo.create_with_array(
                            person_id=person_id,
                            photo_id=photo_map['photo_id'],
                            embedding_array=photo_map['embedding']
                        )
                        stats['embeddings_saved'] += 1
                        logger.info(f"Embedding creado para persona {person_id} en foto {photo_map['photo_id']}")
                    else:
                        logger.info(f"Embedding ya existe para persona {person_id} en foto {photo_map['photo_id']}")
                    
                    # Verificar si la relación ya existe antes de crearla
                    if not photo_people_repo.exists_relationship(photo_map['photo_id'], person_id):
                        # Crear relación foto-persona
                        photo_people_repo.create({
                            'photo_id': photo_map['photo_id'],
                            'person_id': person_id
                        })
                        logger.info(f"Relación foto-persona creada: foto {photo_map['photo_id']} - persona {person_id}")
                    else:
                        logger.info(f"Relación foto-persona ya existe: foto {photo_map['photo_id']} - persona {person_id}")
                    
                    logger.info(f"Embedding y relación guardados exitosamente")
                    
                except Exception as e:
                    logger.error(f"Error guardando embedding: {str(e)}", exc_info=True)
                    stats['errors'] += 1
            
            # Actualizar el embedding promedio de la persona con todos sus embeddings
            try:
                logger.info(f"Actualizando embedding promedio para persona {person_id}")
                new_avg_embedding = face_embedding_repo.get_average_embedding(person_id)
                if new_avg_embedding:
                    person_repo.update_avg_embedding(person_id, new_avg_embedding)
                    logger.info(f"Embedding promedio actualizado para persona {person_id}")
                    print(f"📊 Embedding promedio actualizado para persona {person_id}")
                else:
                    logger.warning(f"No se pudo calcular embedding promedio para persona {person_id}")
            except Exception as e:
                logger.error(f"Error actualizando embedding promedio: {str(e)}", exc_info=True)
                stats['errors'] += 1
            
            stats['clusters_created'] += 1
        
        logger.info("Lote procesado exitosamente")
        print(f"✅ Lote procesado exitosamente")
        
    except Exception as e:
        logger.error(f"Error procesando lote: {str(e)}", exc_info=True)
        stats['errors'] += 1
    
    finally:
        session.close()
    
    return stats

def process_all_faces(photos: List[Dict], batch_size: int = 100) -> Dict:
    """
    Procesa todas las fotos en lotes usando clustering de rostros.
    
    Args:
        photos: Lista completa de fotos
        batch_size: Tamaño del lote para procesamiento
        
    Returns:
        Diccionario con estadísticas totales
    """
    print(f"🚀 Iniciando procesamiento de rostros...")
    print(f"📸 Total de fotos: {len(photos)}")
    print(f"📦 Tamaño de lote: {batch_size}")
    print("-" * 50)
    
    total_stats = {
        'photos_processed': 0,
        'faces_detected': 0,
        'clusters_created': 0,
        'people_created': 0,
        'people_matched': 0,
        'embeddings_saved': 0,
        'errors': 0,
        'batches_processed': 0
    }
    
    # Procesar en lotes
    for i in range(0, len(photos), batch_size):
        batch = photos[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"\n📦 Procesando lote #{batch_num} ({len(batch)} fotos)...")
        
        batch_stats = process_faces_in_batch(batch, batch_size)
        
        # Acumular estadísticas
        for key in total_stats:
            if key in batch_stats:
                total_stats[key] += batch_stats[key]
        
        total_stats['batches_processed'] += 1
        
        print(f"📊 Lote #{batch_num} completado:")
        print(f"   ✅ Fotos procesadas: {batch_stats['photos_processed']}")
        print(f"   👤 Rostros detectados: {batch_stats['faces_detected']}")
        print(f"   🎯 Clusters creados: {batch_stats['clusters_created']}")
        print(f"   👤 Personas creadas: {batch_stats['people_created']}")
        print(f"   🔄 Personas asignadas: {batch_stats['people_matched']}")
        print(f"   💾 Embeddings guardados: {batch_stats['embeddings_saved']}")
        print(f"   ❌ Errores: {batch_stats['errors']}")
    
    # Mostrar resumen final
    print(f"\n🎉 Procesamiento completado!")
    print(f"=" * 50)
    print(f"📊 RESUMEN FINAL:")
    print(f"   📦 Lotes procesados: {total_stats['batches_processed']}")
    print(f"   📸 Fotos procesadas: {total_stats['photos_processed']}")
    print(f"   👤 Rostros detectados: {total_stats['faces_detected']}")
    print(f"   🎯 Clusters creados: {total_stats['clusters_created']}")
    print(f"   👤 Personas creadas: {total_stats['people_created']}")
    print(f"   🔄 Personas asignadas: {total_stats['people_matched']}")
    print(f"   💾 Embeddings guardados: {total_stats['embeddings_saved']}")
    print(f"   ❌ Errores: {total_stats['errors']}")
    
    return total_stats 