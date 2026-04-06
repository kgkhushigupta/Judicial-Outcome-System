"""
Case Embeddings Module
Generates BERT and Sentence-Transformers embeddings for legal cases
Supports both legal embeddings (InLegalBERT) and general embeddings
"""

import logging
import numpy as np
from typing import Optional, List
import warnings

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')


class CaseEmbedder:
    """Generate embeddings for legal cases using Sentence-Transformers and legal models."""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2', use_legal_model: bool = False):
        """
        Initialize case embedder with Sentence-Transformers.
        
        Args:
            model_name: Pre-trained Sentence-Transformers model name
            use_legal_model: Use InLegalBERT (legal-specific) if True
        """
        self.model_name = model_name
        self.use_legal_model = use_legal_model
        self.model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use legal model if requested
            if use_legal_model:
                try:
                    # InLegalBERT for legal domain
                    model_name = "InLegalBERT/InLegalBERT"
                    logger.info("Loading InLegalBERT (legal-specific embeddings)...")
                except:
                    logger.info(f"Using general Sentence-Transformers: {model_name}")
            
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"✓ Loaded embeddings model: {model_name} (dim={self.embedding_dim})")
            
        except ImportError:
            logger.error("sentence-transformers not installed: pip install sentence-transformers")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model = None
    
    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text (case summary or full text)
            
        Returns:
            Embedding vector (numpy array) or None if error
        """
        if self.model is None:
            logger.error("Model not initialized")
            return self._fallback_embedding(text)
        
        try:
            # Use Sentence-Transformers to encode
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return self._fallback_embedding(text)
    
    def embed_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors (numpy arrays)
        """
        if self.model is None:
            logger.warning("Model not initialized, generating dummy embeddings")
            return [self._fallback_embedding(text) for text in texts]
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            logger.info(f"✓ Generated {len(embeddings)} embeddings using Sentence-Transformers")
            return embeddings
        
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}, using fallback")
            return [self._fallback_embedding(text) for text in texts]
    
    def embed_batch_with_similarity(self, texts: List[str], query: str = None):
        """
        Generate embeddings and compute similarity if query provided.
        """
        embeddings = self.embed_batch(texts)
        
        if query is not None and self.model is not None:
            try:
                query_embedding = self.model.encode(query, convert_to_numpy=True)
                similarities = []
                for emb in embeddings:
                    sim = np.dot(emb, query_embedding) / (np.linalg.norm(emb) * np.linalg.norm(query_embedding))
                    similarities.append(sim)
                return embeddings, similarities
            except:
                pass
        
        return embeddings, None
    
    def _fallback_embedding(self, text: str) -> np.ndarray:
        """
        Generate simple TF-based embedding as fallback.
        Creates a 384-dimensional vector from text statistics.
        """
        # Simple fallback: use text statistics as embedding features
        text_lower = text.lower()
        words = text_lower.split()
        
        # Create embedding from word frequencies
        embedding = np.zeros(self.embedding_dim)
        
        if words:
            # Use word lengths and positions as features
            for i, word in enumerate(words[:self.embedding_dim]):
                embedding[i] = len(word) / 20.0  # Normalize by max typical word length
        
        # Add text statistics
        if len(embedding) > 10:
            embedding[0] = len(words) / 1000.0
            embedding[1] = len(text) / 10000.0
        
        return embedding


if __name__ == "__main__":
    embedder = CaseEmbedder()
    
    # Test single embedding
    test_text = "The defendant was charged with fraud and found guilty after presentation of evidence."
    emb = embedder.embed_text(test_text)
    if emb is not None:
        print(f"Single embedding shape: {emb.shape}")
    
    # Test batch embedding
    texts = [
        "Case about theft conviction",
        "Assault charges with witness testimony",
        "Contract dispute resolution"
    ]
    batch_emb = embedder.embed_batch(texts)
    print(f"Batch embeddings: {len(batch_emb)} vectors of shape {batch_emb[0].shape if batch_emb else 'N/A'}")
