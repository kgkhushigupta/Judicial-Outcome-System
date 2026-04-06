"""
FAISS Index Module
Creates and manages vector index for similarity search
"""

import logging
import numpy as np
from typing import Optional, List

logger = logging.getLogger(__name__)


class FAISSIndex:
    """Manage FAISS vector index for efficient similarity search."""
    
    def __init__(self, dimension: int = 768, index_type: str = 'flat'):
        """
        Initialize FAISS index.
        
        Args:
            dimension: Embedding dimension
            index_type: Type of index ('flat', 'ivf', 'hnsw')
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.id_map = {}
        self.init_index()
        logger.info(f"FAISSIndex initialized with {index_type} index")
    
    def init_index(self):
        """Initialize FAISS index."""
        try:
            import faiss
            
            if self.index_type == 'flat':
                self.index = faiss.IndexFlatL2(self.dimension)
            else:
                logger.warning(f"Index type {self.index_type} not fully implemented")
                self.index = faiss.IndexFlatL2(self.dimension)
        
        except ImportError:
            logger.warning("FAISS not installed. Install with: pip install faiss-cpu")
            self.index = None
    
    def add_vectors(self, vectors: np.ndarray, ids: Optional[List[int]] = None) -> bool:
        """
        Add vectors to index.
        
        Args:
            vectors: Array of vectors (n_samples, dimension)
            ids: Optional list of vector IDs
            
        Returns:
            True if successful
        """
        if self.index is None:
            logger.error("FAISS index not initialized")
            return False
        
        try:
            # Convert to float32 for FAISS
            vectors = vectors.astype('float32')
            
            # Add to index
            self.index.add(vectors)
            
            # Map IDs
            if ids:
                for i, id_ in enumerate(ids):
                    self.id_map[len(self.id_map)] = id_
            
            logger.info(f"Added {len(vectors)} vectors to index")
            return True
        
        except Exception as e:
            logger.error(f"Error adding vectors: {str(e)}")
            return False
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> tuple:
        """
        Search for k nearest neighbors.
        
        Args:
            query_vector: Query vector
            k: Number of results
            
        Returns:
            Tuple of (distances, indices)
        """
        if self.index is None:
            logger.error("FAISS index not initialized")
            return None, None
        
        try:
            query_vector = query_vector.astype('float32').reshape(1, -1)
            distances, indices = self.index.search(query_vector, k)
            return distances[0], indices[0]
        
        except Exception as e:
            logger.error(f"Error searching index: {str(e)}")
            return None, None
    
    def save(self, filepath: str) -> bool:
        """Save index to disk."""
        if self.index is None:
            return False
        
        try:
            import faiss
            faiss.write_index(self.index, filepath)
            logger.info(f"Index saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            return False
    
    def load(self, filepath: str) -> bool:
        """Load index from disk."""
        try:
            import faiss
            self.index = faiss.read_index(filepath)
            logger.info(f"Index loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            return False


if __name__ == "__main__":

    print("Testing FAISS Index...")

    # Create FAISS index
    index = FAISSIndex(dimension=768)

    # Create dummy embeddings (10 vectors of size 768)
    vectors = np.random.rand(10, 768)

    # Add vectors to index
    index.add_vectors(vectors)


    print("Vectors added to index")

    # Create a query vector
    query = np.random.rand(768)

    # Search for similar vectors
    distances, indices = index.search(query, k=3)

    print("Search Results")
    print("Indices:", indices)
    print("Distances:", distances)
