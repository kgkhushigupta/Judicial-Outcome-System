"""
Similarity Search Module
Performs semantic similarity search on legal cases
"""

import logging
from typing import List, Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)


class SimilaritySearch:
    """Perform semantic similarity search on judicial cases."""
    
    def __init__(self, embedder, faiss_index):
        """
        Initialize similarity search.
        
        Args:
            embedder: Case embedder instance
            faiss_index: FAISS index instance
        """
        self.embedder = embedder
        self.index = faiss_index
        self.case_database = {}
        logger.info("SimilaritySearch initialized")
    
    def index_case(self, case_id: str, case_text: str) -> bool:
        """
        Index a case for similarity search.
        
        Args:
            case_id: Unique case identifier
            case_text: Full or summary text of case
            
        Returns:
            True if successful
        """
        try:
            # Generate embedding
            embedding = self.embedder.embed_text(case_text)
            if embedding is None:
                return False
            
            # Add to FAISS index
            self.index.add_vectors(
                np.array([embedding]),
                ids=[case_id]
            )
            
            # Store metadata
            self.case_database[case_id] = {
                'text': case_text,
                'embedding': embedding
            }
            
            return True
        
        except Exception as e:
            logger.error(f"Error indexing case {case_id}: {str(e)}")
            return False
    
    def find_similar_cases(self, query_text: str, k: int = 5) -> List[Dict]:
        """
        Find similar cases to query text.
        
        Args:
            query_text: Query case text
            k: Number of similar cases to return
            
        Returns:
            List of similar cases with scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed_text(query_text)
            if query_embedding is None:
                return []
            
            # Search FAISS index
            distances, indices = self.index.search(query_embedding, k)
            
            results = []
            for distance, idx in zip(distances, indices):
                if idx >= 0:  # Valid result
                    results.append({
                        'distance': float(distance),
                        'similarity_score': 1.0 / (1.0 + distance),
                        'index_position': int(idx)
                    })
            
            logger.info(f"Found {len(results)} similar cases")
            return results
        
        except Exception as e:
            logger.error(f"Error searching similar cases: {str(e)}")
            return []

if __name__ == "__main__":

    print("Testing Similarity Search System...\n")

    # Import required modules
    from src.embeddings.case_embeddings import CaseEmbedder
    from src.similarity.faiss_index import FAISSIndex

    # Initialize components
    embedder = CaseEmbedder()
    faiss_index = FAISSIndex(dimension=768)

    search_engine = SimilaritySearch(embedder, faiss_index)

    # Sample legal cases
    cases = {
        "C1": "The accused committed fraud under IPC section 420.",
        "C2": "This case involves breach of contract between two companies.",
        "C3": "The defendant was charged with financial fraud and cheating.",
        "C4": "Dispute regarding property ownership and inheritance law.",
        "C5": "Criminal charges for fraudulent financial transactions."
    }

    # Index the cases
    print("Indexing cases...")
    for case_id, text in cases.items():
        search_engine.index_case(case_id, text)

    print("Cases indexed successfully.\n")

    # Query
    query = "Fraud under IPC law"

    print("Query:", query)
    print("\nSearching for similar cases...\n")

    results = search_engine.find_similar_cases(query, k=3)

    # Print results
    for i, result in enumerate(results, 1):
        print(f"Result {i}")
        print("Index Position:", result["index_position"])
        print("Distance:", result["distance"])
        print("Similarity Score:", result["similarity_score"])
        print()
