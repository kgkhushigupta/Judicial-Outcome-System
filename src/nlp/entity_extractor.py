"""
Entity Extraction Module
Extracts key entities (names, laws, dates) from legal documents
"""

import re
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an extracted entity."""
    text: str
    entity_type: str
    confidence: float = 1.0


class EntityExtractor:
    """Extract named entities from legal documents."""
    
    def __init__(self, use_external_ner: bool = False):
        """
        Initialize entity extractor.
        
        Args:
            use_external_ner: Use external NER model (spaCy, etc.)
        """
        self.use_external_ner = use_external_ner
        self.nlp = None
        
        if use_external_ner:
            try:
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("Loaded spaCy model")
            except ImportError:
                logger.warning("spaCy not installed. Using regex-based extraction.")
                self.use_external_ner = False
        
        logger.info("EntityExtractor initialized")
    
    def extract_persons(self, text: str) -> List[str]:
        """Extract person names from text."""
        # Pattern for capitalized names
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        matches = re.findall(pattern, text)
        return list(set(matches))[:20]  # Top 20 unique names
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # DD-MM-YYYY
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}'
        ]
        
        dates = []
        for pattern in patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(dates))
    
    def extract_laws(self, text: str) -> List[str]:
        """Extract law references and statutes."""
        pattern = r'(?:Section|Act|Article|Rule)\s+\d+(?:[A-Z])?'
        matches = re.findall(pattern, text)
        return list(set(matches))
    
    def extract_all_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all entity types from text.
        
        Args:
            text: Input document
            
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        entities = {
            'persons': self.extract_persons(text),
            'dates': self.extract_dates(text),
            'laws': self.extract_laws(text)
        }
        
        logger.info(f"Extracted entities: {sum(len(v) for v in entities.values())} total")
        return entities


if __name__ == "__main__":
    extractor = EntityExtractor()
