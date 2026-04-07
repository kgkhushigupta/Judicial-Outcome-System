import numpy as np
import logging

logger = logging.getLogger(__name__)

try:
    import faiss
    FAISS_AVAILABLE = True
    logger.info("[FAISS] faiss-cpu loaded successfully.")
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("[FAISS] faiss-cpu not available. Using numpy cosine similarity fallback.")


class FAISSIndex:
    def __init__(self, dim=384):
        self.dim = dim
        self.metadata = []
        self.embeddings = None
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatIP(dim)
        else:
            self.index = None

    def build(self, embeddings, metadata):
        embeddings = np.array(embeddings, dtype=np.float32)
        self.embeddings = embeddings.copy()
        self.metadata = metadata

        if FAISS_AVAILABLE:
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
            logger.info("[FAISS] Index built with %d vectors, dim=%d", len(embeddings), self.dim)
        else:
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            self.embeddings = self.embeddings / (norms + 1e-8)
            logger.info("[FAISS-Fallback] Stored %d normalized vectors for cosine search.", len(embeddings))

    def search(self, query_embedding, top_k=3):
        query_embedding = np.array(query_embedding, dtype=np.float32).reshape(1, -1)

        if FAISS_AVAILABLE:
            faiss.normalize_L2(query_embedding)
            distances, indices = self.index.search(query_embedding, top_k)
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                res = self.metadata[idx].copy()
                res['similarity'] = round(float(dist) * 100, 2)
                results.append(res)
        else:
            similarities = np.dot(self.embeddings, query_embedding.T).flatten()
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            results = []
            for idx in top_indices:
                res = self.metadata[idx].copy()
                res['similarity'] = round(float(similarities[idx]) * 100, 2)
                results.append(res)

        logger.info("[FAISS] Retrieved %d precedents. Top similarity: %.2f%%",
                   len(results), results[0]['similarity'] if results else 0)
        return results

    def get_index_info(self):
        return {
            "faiss_available": FAISS_AVAILABLE,
            "index_size": self.index.ntotal if FAISS_AVAILABLE and self.index else
                         len(self.embeddings) if self.embeddings is not None else 0,
            "dimension": self.dim
        }
