from typing import List
import logging
from sentence_transformers import SentenceTransformer
from config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Successfully loaded model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        try:
            if not texts:
                return []
                
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            
            print(f"\n--- EMBEDDING SERVICE DEBUG ---")
            print(f"Raw embeddings type from model: {type(embeddings)}")
            print(f"Raw embeddings shape: {embeddings.shape if hasattr(embeddings, 'shape') else 'N/A'}")
            
            # Convert to list of lists (numpy array to nested list)
            embeddings_list = embeddings.tolist()
            
            print(f"✓ Generated {len(embeddings_list)} embeddings")
            print(f"✓ After .tolist() type: {type(embeddings_list)}")
            print(f"✓ First embedding type: {type(embeddings_list[0]) if embeddings_list else None}")
            print(f"✓ First embedding sample (first 5 values): {embeddings_list[0][:5] if embeddings_list else None}")
            print(f"✓ Embedding dtype check: {[type(v) for v in embeddings_list[0][:3]] if embeddings_list else None}")
            print(f"--- END DEBUG ---\n")
            
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.get_embeddings([text])[0]
