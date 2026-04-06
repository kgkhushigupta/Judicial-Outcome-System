"""
PDF Extraction Module
Handles extraction of text from PDF documents using Apache Tika
"""

import logging
import os
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text content from PDF court judgment documents using Apache Tika."""
    
    def __init__(self, tika_path: Optional[str] = None):
        """
        Initialize PDF extractor with Tika.
        
        Args:
            tika_path: Path to Apache Tika server (optional)
        """
        self.tika_path = tika_path
        self.use_tika = self._check_tika_available()
        
        if self.use_tika:
            logger.info("✓ Apache Tika initialized for PDF extraction")
        else:
            logger.info("⚠ Tika unavailable, using fallback PDF extraction")
    
    def _check_tika_available(self) -> bool:
        """Check if Apache Tika is available"""
        try:
            from tika import parser
            logger.debug("✓ Tika imported successfully")
            return True
        except ImportError:
            logger.debug("⚠ Tika not installed, fallback enabled")
            return False
    
    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from a PDF file using Tika or fallback.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content or None if extraction fails
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        try:
            if self.use_tika:
                return self._extract_with_tika(pdf_path)
            else:
                return self._extract_with_pypdf(pdf_path)
        except Exception as e:
            logger.error(f"Error extracting PDF {pdf_path}: {str(e)}")
            return None
    
    def _extract_with_tika(self, pdf_path: str) -> Optional[str]:
        """Extract using Apache Tika"""
        try:
            from tika import parser as tika_parser
            
            raw = tika_parser.from_file(pdf_path)
            text = raw.get("content", "")
            
            logger.info(f"✓ Extracted {len(text)} chars from {os.path.basename(pdf_path)} (Tika)")
            return text
        except Exception as e:
            logger.warning(f"Tika extraction failed, fallback enabled: {e}")
            return self._extract_with_pypdf(pdf_path)
    
    def _extract_with_pypdf(self, pdf_path: str) -> Optional[str]:
        """Fallback extraction using PyPDF2"""
        try:
            import PyPDF2
            
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            logger.info(f"✓ Extracted {len(text)} chars from {os.path.basename(pdf_path)} (PyPDF2)")
            return text if text else None
        except Exception as e:
            logger.error(f"PyPDF2 extraction also failed: {e}")
            return None
    
    def extract_metadata(self, pdf_path: str) -> Dict:
        """Extract metadata (title, author, date, etc.)"""
        try:
            if self.use_tika:
                from tika import parser as tika_parser
                raw = tika_parser.from_file(pdf_path)
                return raw.get("metadata", {})
            else:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    return dict(reader.metadata) if reader.metadata else {}
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}
    
    def batch_extract(self, pdf_dir: str) -> Dict:
        """
        Extract text from multiple PDF files.
        
        Args:
            pdf_dir: Directory containing PDF files
            
        Returns:
            Dictionary mapping filenames to extracted text
        """
        extracted_docs = {}
        pdf_path = Path(pdf_dir)
        
        if not pdf_path.exists():
            logger.warning(f"PDF directory not found: {pdf_dir}")
            return extracted_docs
        
        pdf_files = list(pdf_path.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {pdf_dir}")
        
        for pdf_file in pdf_files:
            text = self.extract_text(str(pdf_file))
            if text:
                metadata = self.extract_metadata(str(pdf_file))
                extracted_docs[pdf_file.name] = {
                    "text": text,
                    "metadata": metadata,
                    "pages": len(text.split('\n')) // 30  # Rough estimate
                }
        
        logger.info(f"✓ Successfully extracted {len(extracted_docs)} documents")
        return extracted_docs


if __name__ == "__main__":
    # Test extraction
    logger.basicConfig(level=logging.INFO)
    extractor = PDFExtractor()
    
    # Example usage
    test_pdf = "sample.pdf"
    if os.path.exists(test_pdf):
        text = extractor.extract_text(test_pdf)
        print(f"Extracted {len(text) if text else 0} characters")
    
    # Batch extraction
    pdf_dir = "data/pdfs"
    if os.path.exists(pdf_dir):
        docs = extractor.batch_extract(pdf_dir)
        print(f"Extracted {len(docs)} documents from {pdf_dir}")
