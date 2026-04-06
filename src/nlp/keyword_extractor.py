"""
Keyword Extraction Module
Extracts important keywords and phrases from court judgments
Critical for: clustering, knowledge graph, similarity search
"""

import logging
import re
from typing import List, Dict, Tuple, Optional
from collections import Counter
import math

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Extract important keywords from legal documents for clustering, KG, and similarity search."""
    
    LEGAL_STOPWORDS = {
        'the', 'a', 'an', 'and', 'or', 'of', 'in', 'for', 'on', 'is', 'are',
        'shall', 'will', 'may', 'can', 'court', 'case', 'law', 'legal', 'act',
        'that', 'this', 'it', 'to', 'be', 'by', 'from', 'with', 'as', 'at',
        'was', 'were', 'been', 'have', 'has', 'do', 'does', 'did', 'would',
        'should', 'could', 'must', 'also', 'such', 'any', 'all', 'each'
    }
    
    LEGAL_KEYWORDS_BOOST = {
        'murder': 2.0, 'theft': 2.0, 'fraud': 2.0, 'rape': 2.0,
        'section': 1.5, 'article': 1.5, 'judgment': 1.8, 'verdict': 1.8,
        'defendant': 1.5, 'plaintiff': 1.5, 'witness': 1.5, 'evidence': 1.8,
        'guilty': 1.8, 'innocent': 1.8, 'sentence': 1.8, 'conviction': 1.8
    }
    
    def __init__(self, num_keywords: int = 15, phrase_length: int = 2):
        """
        Initialize keyword extractor.
        
        Args:
            num_keywords: Number of top keywords to extract
            phrase_length: Length of n-grams to extract
        """
        self.num_keywords = num_keywords
        self.phrase_length = phrase_length
        logger.info(f"KeywordExtractor initialized (top {num_keywords} keywords)")
    
    def extract_keywords(self, text: str, use_idf: bool = True) -> List[str]:
        """
        Extract keywords using TF-IDF-like approach.
        
        Args:
            text: Input document
            use_idf: Use IDF weighting for legal terms
            
        Returns:
            List of top keywords sorted by importance
        """
        # Clean and tokenize
        words = text.lower().split()
        words = [re.sub(r'[.,!?;:\'"()]', '', w) for w in words]
        
        # Filter stopwords and short words
        words = [
            w for w in words 
            if w not in self.LEGAL_STOPWORDS and len(w) > 3
        ]
        
        # Count frequencies
        word_counts = Counter(words)
        
        # Apply legal keyword boost
        if use_idf:
            for word in word_counts:
                boost = self.LEGAL_KEYWORDS_BOOST.get(word, 1.0)
                word_counts[word] *= boost
        
        # Get top keywords
        top_keywords = [word for word, _ in word_counts.most_common(self.num_keywords)]
        
        logger.info(f"Extracted {len(top_keywords)} keywords from {len(word_counts)} unique terms")
        return top_keywords
    
    def extract_keywords_with_scores(self, text: str) -> List[Tuple[str, float]]:
        """
        Extract keywords with TF-IDF scores.
        
        Args:
            text: Input document
            
        Returns:
            List of (keyword, score) tuples
        """
        words = text.lower().split()
        words = [re.sub(r'[.,!?;:\'"()]', '', w) for w in words]
        words = [w for w in words if w not in self.LEGAL_STOPWORDS and len(w) > 3]
        
        # Calculate TF
        total_words = len(words)
        word_counts = Counter(words)
        tf_scores = {word: count / total_words for word, count in word_counts.items()}
        
        # Apply legal boost as IDF approximation
        final_scores = []
        for word, tf_score in tf_scores.items():
            boost = self.LEGAL_KEYWORDS_BOOST.get(word, 1.0)
            final_score = tf_score * boost
            final_scores.append((word, final_score))
        
        # Sort by score
        final_scores.sort(key=lambda x: x[1], reverse=True)
        return final_scores[:self.num_keywords]
    
    def extract_phrases(self, text: str, phrase_length: Optional[int] = None) -> List[str]:
        """
        Extract key phrases (n-grams).
        
        Args:
            text: Input document
            phrase_length: Length of phrases to extract (default: self.phrase_length)
            
        Returns:
            List of key phrases sorted by frequency
        """
        if phrase_length is None:
            phrase_length = self.phrase_length
            
        words = text.lower().split()
        words = [re.sub(r'[.,!?;:\'"()]', '', w) for w in words]
        
        # Extract n-grams
        phrases = []
        for i in range(len(words) - phrase_length + 1):
            phrase = ' '.join(words[i:i+phrase_length])
            # Filter out phrases with stopwords only
            if not all(w in self.LEGAL_STOPWORDS for w in phrase.split()):
                phrases.append(phrase)
        
        # Count and return top phrases
        phrase_counts = Counter(phrases)
        top_phrases = [p for p, _ in phrase_counts.most_common(self.num_keywords)]
        
        logger.info(f"Extracted {len(top_phrases)} top phrases")
        return top_phrases
    
    def extract_all(self, text: str) -> Dict[str, any]:
        """
        Extract keywords, phrases, and scores in one call.
        Used for: clustering, KG, similarity search
        
        Args:
            text: Input document
            
        Returns:
            Dictionary with keywords, phrases, and scores
        """
        keywords = self.extract_keywords(text)
        keywords_scored = self.extract_keywords_with_scores(text)
        phrases = self.extract_phrases(text)
        
        return {
            'keywords': keywords,
            'keywords_scored': keywords_scored,
            'phrases': phrases,
            'top_keyword': keywords[0] if keywords else None,
            'keyword_count': len(keywords)
        }


if __name__ == "__main__":
    extractor = KeywordExtractor()
    
    # Test with sample legal text
    sample_text = "Section 420 IPC: Cheating and fraud. The defendant was found guilty of theft and fraud."
    print("\n" + "="*60)
    print("KEYWORD EXTRACTION TEST")
    print("="*60)
    print(f"\nInput: {sample_text}\n")
    
    result = extractor.extract_all(sample_text)
    print(f"Keywords: {result['keywords']}")
    print(f"Top Keyword: {result['top_keyword']}")
    print(f"Phrases: {result['phrases'][:5]}")
    print("\n" + "="*60)
