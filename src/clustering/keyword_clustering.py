"""
Keyword Clustering Module
Clusters similar legal cases based on keywords and patterns
"""

import logging
from typing import List, Dict
import numpy as np

logger = logging.getLogger(__name__)


class KeywordClusterer:
    """Cluster legal cases based on keywords and similarity."""
    
    def __init__(self, n_clusters: int = 5, method: str = 'kmeans'):
        """
        Initialize keyword clusterer.
        
        Args:
            n_clusters: Number of clusters
            method: Clustering method ('kmeans', 'hierarchical')
        """
        self.n_clusters = n_clusters
        self.method = method
        
        try:
            from sklearn.cluster import KMeans
            self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        except ImportError:
            logger.warning("scikit-learn not installed")
            self.kmeans = None
        
        logger.info(f"KeywordClusterer initialized with {method} clustering")
    
    def cluster_cases(self, case_vectors: np.ndarray) -> np.ndarray:
        """
        Cluster cases based on vector representations.
        
        Args:
            case_vectors: Array of case embeddings/vectors
            
        Returns:
            Array of cluster assignments
        """
        if self.kmeans is None:
            logger.error("Clustering not available")
            return None
        
        labels = self.kmeans.fit_predict(case_vectors)
        logger.info(f"Clustered cases into {self.n_clusters} clusters")
        return labels
    
    def get_cluster_centers(self) -> np.ndarray:
        """Get cluster centers."""
        if self.kmeans is None:
            return None
        return self.kmeans.cluster_centers_
    
    def assign_new_case(self, case_vector: np.ndarray) -> int:
        """
        Assign a new case to nearest cluster.
        
        Args:
            case_vector: Vector representation of case
            
        Returns:
            Cluster label
        """
        if self.kmeans is None:
            return -1
        return self.kmeans.predict([case_vector])[0]


if __name__ == "__main__":
    print("Testing Keyword Clustering...")

    # Create dummy case embeddings (10 cases, 5 features each)
    dummy_vectors = np.random.rand(10, 5)

    clusterer = KeywordClusterer(n_clusters=3)

    labels = clusterer.cluster_cases(dummy_vectors)

    print("Cluster Labels:")
    print(labels)

    print("Cluster Centers:")
    print(clusterer.get_cluster_centers())
