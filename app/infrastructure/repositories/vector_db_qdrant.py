from typing import List, Tuple
from app.domain.repositories.vector_repository import VectorRepository
from qdrant_client import QdrantClient


class VectorDBQdrant(VectorRepository):
    def __init__(self,
        collection_name: str,
        vector_size: int,
        url: str = "http://localhost:6333",
        api_key: str = "super_secret_api_key",
        distance: str = "Cosine"):
        self.client: QdrantClient = QdrantClient(
          url=url,
          api_key=api_key
      )
        self.collection_name: str = collection_name
        self.vector_size: int = vector_size
        self.distance: str = distance
        self._create_collection()
    
    def _create_collection(self):
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(self.collection_name,
            vectors_config={
                "size": self.vector_size,
                "distance": self.distance
            }
            )

    def add_vector(self, vector: List[float], id: str):
        self.client.upsert(
            collection_name=self.collection_name,
            points=[{"id": id, "vector": vector}],
        )
        self.client.add(self.collection_name, vector)

    def search_ids(self, vector: List[float],top_k: int=10) ->Tuple[bool, List[str] | None, str]:
        try:
            results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
                    limit=top_k,
                )
            ids = [str(r.id)for r in results]
            return True, ids, ""
        except Exception as e:
            return False, None, f"Error al buscar los IDs:"