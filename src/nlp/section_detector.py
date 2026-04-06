"""
Section Detection Module
Identifies and extracts different sections from court judgments
"""

import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SectionDetector:
    """Detect and extract sections from legal documents."""
    
    # Common section patterns in court judgments
    SECTION_PATTERNS = {
        'facts': r'(?:facts|case facts|background|circumstances)',
        'issues': r'(?:issues|issues for consideration|questions of law)',
        'arguments': r'(?:arguments|submissions|counsel|submissions of)',
        'reasoning': r'(?:reasoning|analysis|discussion|held|observation)',
        'judgment': r'(?:judgment|order|decision|held|verdict)',
        'conclusion': r'(?:conclusion|conclusions|concluding remarks)'
    }
    
    def __init__(self):
        """Initialize section detector."""
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.SECTION_PATTERNS.items()
        }
        logger.info("SectionDetector initialized")
    
    def detect_sections(self, text: str) -> Dict[str, Optional[str]]:
        """
        Detect and extract sections from document.
        
        Args:
            text: Full document text
            
        Returns:
            Dictionary mapping section names to section content
        """
        sections = {}
        lines = text.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            # Check if line matches any section header
            matched_section = None
            for section_name, pattern in self.compiled_patterns.items():
                if pattern.search(line) and len(line) < 100:  # Likely a header
                    matched_section = section_name
                    break
            
            if matched_section:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                
                current_section = matched_section
                section_content = []
            else:
                section_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(section_content).strip()
        
        logger.info(f"Detected {len(sections)} sections")
        return sections
    
    def get_section(self, text: str, section_name: str) -> Optional[str]:
        """Extract a specific section from document."""
        sections = self.detect_sections(text)
        return sections.get(section_name)


if __name__ == "__main__":
    detector = SectionDetector()
