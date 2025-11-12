from app.domain.interfaces.embedding_service import EmbeddingService
from sentence_transformers import SentenceTransformer
from PIL import Image
import io

from typing import List, Tuple


class EmbeddingServiceImpl(EmbeddingService):

  def __init__(self, model_name: str = "clip-ViT-B-32"):
        self.model = SentenceTransformer(model_name)

  def get_embedding(self, file_content: bytes) -> Tuple[bool, List[float] | None, str]:
    try:
        print(f"type(file_content): {type(file_content)}")
        image = Image.open(io.BytesIO(file_content)).convert("RGB")
        embedding = self.model.encode(image, convert_to_numpy=True)
        return True, embedding.tolist(), ""
    except Exception as e:
        return False, None, f"Error al obtener el embedding: {e}"