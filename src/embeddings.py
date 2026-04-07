import numpy as np
import logging

logger = logging.getLogger(__name__)


class LegalEmbedder:
    def __init__(self, model_name="law-ai/InLegalBERT"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("[Embeddings] Loading model: %s", self.model_name)
            self.model = SentenceTransformer(self.model_name)
            logger.info("[Embeddings] Model loaded successfully. Embedding dim: %d",
                       self.model.get_sentence_embedding_dimension())
        except Exception as e:
            logger.warning("[Embeddings] Failed to load %s: %s", self.model_name, str(e))
            try:
                fallback = "sentence-transformers/all-MiniLM-L6-v2"
                logger.info("[Embeddings] Trying fallback model: %s", fallback)
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(fallback)
                self.model_name = fallback
                logger.info("[Embeddings] Fallback model loaded. Dim: %d",
                           self.model.get_sentence_embedding_dimension())
            except Exception as e2:
                logger.error("[Embeddings] All models failed: %s. Using random embeddings.", str(e2))
                self.model = None

    def encode(self, texts, batch_size=32):
        if not texts:
            return np.array([])

        clean_texts = [str(t)[:512] if t else "" for t in texts]

        if self.model is not None:
            try:
                embeddings = self.model.encode(
                    clean_texts,
                    batch_size=batch_size,
                    show_progress_bar=len(clean_texts) > 100,
                    convert_to_numpy=True
                )
                logger.info("[Embeddings] Encoded %d texts -> shape %s", len(texts), str(embeddings.shape))
                return embeddings
            except Exception as e:
                logger.error("[Embeddings] Encoding failed: %s. Using random.", str(e))

        dim = 384
        np.random.seed(42)
        embeddings = np.random.randn(len(texts), dim).astype(np.float32)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / (norms + 1e-8)
        logger.warning("[Embeddings] Generated random embeddings: (%d, %d)", len(texts), dim)
        return embeddings

    def get_model_info(self):
        return {
            "model_name": self.model_name,
            "model_loaded": self.model is not None,
            "embedding_dim": self.model.get_sentence_embedding_dimension() if self.model else 384
        }
