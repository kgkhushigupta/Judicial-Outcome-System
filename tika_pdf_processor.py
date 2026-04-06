"""
Enhanced PDF Ingestion System with Apache Tika
Handles PDF document extraction, metadata parsing, and bulk processing
"""

import os
import logging
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TikaDocumentProcessor:
    """Process documents using Apache Tika with multiple fallbacks"""
    
    def __init__(self, enable_tika: bool = True, fallback_chain: List[str] = None):
        """
        Initialize Tika processor
        
        Args:
            enable_tika: Enable Tika processing
            fallback_chain: List of fallback methods
        """
        self.enable_tika = enable_tika
        self.fallback_chain = fallback_chain or ["pypdf2", "fitz", "pdfplumber", "text_extraction"]
        self.extraction_stats = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "extraction_methods": {}
        }
        self._verify_tika()
    
    def _verify_tika(self) -> bool:
        """Verify Tika installation and availability"""
        if not self.enable_tika:
            logger.info("⚠ Apache Tika is disabled")
            return False
        
        try:
            # Try to import tika
            import tika
            from tika import parser
            logger.info("✓ Apache Tika is available")
            return True
        except ImportError:
            logger.warning("⚠ Apache Tika not found. Trying to install...")
            try:
                import subprocess
                subprocess.check_call(['pip', 'install', 'tika', '-q'])
                logger.info("✓ Apache Tika installed successfully")
                return True
            except Exception as e:
                logger.warning(f"⚠ Could not install Tika: {e}")
                return False
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[Optional[str], str, Dict]:
        """
        Extract text from PDF using Tika or fallback methods
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            (extracted_text, method_used, metadata)
        """
        if not os.path.exists(pdf_path):
            return None, "error", {"error": "File not found"}
        
        # Try Tika first
        if self.enable_tika:
            try:
                text, metadata = self._extract_with_tika(pdf_path)
                if text:
                    self.extraction_stats["extraction_methods"]["tika"] = \
                        self.extraction_stats["extraction_methods"].get("tika", 0) + 1
                    return text, "tika", metadata
            except Exception as e:
                logger.debug(f"Tika extraction failed: {e}")
        
        # Try fallback methods in order
        for fallback_method in self.fallback_chain:
            try:
                if fallback_method == "pypdf2":
                    text, metadata = self._extract_with_pypdf2(pdf_path)
                elif fallback_method == "fitz":
                    text, metadata = self._extract_with_fitz(pdf_path)
                elif fallback_method == "pdfplumber":
                    text, metadata = self._extract_with_pdfplumber(pdf_path)
                else:
                    continue
                
                if text:
                    self.extraction_stats["extraction_methods"][fallback_method] = \
                        self.extraction_stats["extraction_methods"].get(fallback_method, 0) + 1
                    return text, fallback_method, metadata
            except Exception as e:
                logger.debug(f"{fallback_method} extraction failed: {e}")
        
        return None, "none", {"error": "All extraction methods failed"}
    
    def _extract_with_tika(self, pdf_path: str) -> Tuple[str, Dict]:
        """Extract using Apache Tika"""
        try:
            from tika import parser as tika_parser
            parsed = tika_parser.from_file(pdf_path)
            
            text = parsed.get('content', '')
            metadata = parsed.get('metadata', {})
            
            return text.strip(), metadata
        except Exception as e:
            raise Exception(f"Tika extraction error: {e}")
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Tuple[str, Dict]:
        """Extract using PyPDF2"""
        try:
            import PyPDF2
            text_content = []
            metadata = {}
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata = dict(reader.metadata) if reader.metadata else {}
                
                for page in reader.pages:
                    text_content.append(page.extract_text())
            
            return '\n'.join(text_content), metadata
        except Exception as e:
            raise Exception(f"PyPDF2 extraction error: {e}")
    
    def _extract_with_fitz(self, pdf_path: str) -> Tuple[str, Dict]:
        """Extract using PyMuPDF (fitz)"""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            text_content = []
            metadata = doc.metadata
            
            for page in doc:
                text_content.append(page.get_text())
            
            return '\n'.join(text_content), metadata or {}
        except Exception as e:
            raise Exception(f"Fitz extraction error: {e}")
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Tuple[str, Dict]:
        """Extract using pdfplumber"""
        try:
            import pdfplumber
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                metadata = pdf.metadata
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            return '\n'.join(text_content), metadata or {}
        except Exception as e:
            raise Exception(f"pdfplumber extraction error: {e}")
    
    def process_pdf_directory(self, directory: str) -> List[Dict]:
        """
        Process all PDFs in a directory
        
        Args:
            directory: Path to directory containing PDFs
            
        Returns:
            List of processed document info
        """
        print(f"\n[TIKA] Processing PDFs from: {directory}")
        processed = []
        
        if not os.path.isdir(directory):
            logger.warning(f"Directory not found: {directory}")
            return processed
        
        pdf_files = list(Path(directory).glob("**/*.pdf"))
        print(f"  Found {len(pdf_files)} PDF files")
        
        for pdf_path in pdf_files:
            try:
                self.extraction_stats["total_files"] += 1
                text, method, metadata = self.extract_text_from_pdf(str(pdf_path))
                
                if text:
                    result = {
                        "file": str(pdf_path),
                        "filename": pdf_path.name,
                        "text": text[:1000] + "..." if len(text) > 1000 else text,
                        "extraction_method": method,
                        "metadata": metadata,
                        "text_length": len(text),
                        "pages": len(text.split('\n')) // 50,  # Rough estimate
                        "status": "success"
                    }
                    processed.append(result)
                    self.extraction_stats["successful"] += 1
                    print(f"  ✓ {pdf_path.name} ({method})")
                else:
                    processed.append({
                        "file": str(pdf_path),
                        "status": "failed",
                        "error": "No text extracted"
                    })
                    self.extraction_stats["failed"] += 1
                    print(f"  ✗ {pdf_path.name} (failed)")
            except Exception as e:
                self.extraction_stats["failed"] += 1
                logger.error(f"Error processing {pdf_path}: {e}")
        
        return processed
    
    def extract_legal_entities(self, text: str) -> Dict:
        """
        Extract legal entities and key information from document text
        
        Args:
            text: Extracted document text
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {
            "parties": [],
            "judges": [],
            "dates": [],
            "verdict": None,
            "sentence": None
        }
        
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text[:5000])  # Process first 5000 chars
            
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    entities["parties"].append(ent.text)
                elif ent.label_ == "DATE":
                    entities["dates"].append(ent.text)
            
            # Look for verdict keywords
            text_lower = text.lower()
            if "guilty" in text_lower:
                entities["verdict"] = "Guilty"
            elif "acquitted" in text_lower or "not guilty" in text_lower:
                entities["verdict"] = "Acquitted"
            elif "dismissed" in text_lower:
                entities["verdict"] = "Dismissed"
        except Exception as e:
            logger.debug(f"Entity extraction failed: {e}")
        
        return entities
    
    def get_extraction_stats(self) -> Dict:
        """Get extraction statistics"""
        return {
            **self.extraction_stats,
            "success_rate": round(
                (self.extraction_stats["successful"] / max(1, self.extraction_stats["total_files"])) * 100, 
                2
            )
        }


class PDFDocumentManager:
    """Manage PDF uploads and processing"""
    
    def __init__(self, upload_dir: str = "data/uploads"):
        self.upload_dir = upload_dir
        self.processed_dir = os.path.join(upload_dir, "processed")
        self.failed_dir = os.path.join(upload_dir, "failed")
        
        # Create directories
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.failed_dir, exist_ok=True)
        
        self.processor = TikaDocumentProcessor()
    
    def upload_pdf(self, file_path: str, destination: str = None) -> Dict:
        """
        Upload PDF to system
        
        Args:
            file_path: Path to PDF file
            destination: Optional destination directory
            
        Returns:
            Upload status and metadata
        """
        if not os.path.exists(file_path):
            return {"status": "failed", "error": "File not found"}
        
        destination = destination or self.upload_dir
        filename = os.path.basename(file_path)
        dest_path = os.path.join(destination, filename)
        
        try:
            # Copy file to upload directory
            import shutil
            shutil.copy2(file_path, dest_path)
            
            return {
                "status": "success",
                "filename": filename,
                "path": dest_path,
                "size_kb": round(os.path.getsize(dest_path) / 1024, 2),
                "uploaded_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def process_uploaded_pdfs(self) -> Dict:
        """Process all uploaded PDFs"""
        results = self.processor.process_pdf_directory(self.upload_dir)
        
        # Save processing report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_processed": len(results),
            "documents": results,
            "statistics": self.processor.get_extraction_stats()
        }
        
        report_path = os.path.join(self.processed_dir, "processing_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def get_upload_status(self) -> Dict:
        """Get upload directory status"""
        pdf_files = list(Path(self.upload_dir).glob("*.pdf"))
        return {
            "total_uploads": len(pdf_files),
            "files": [f.name for f in pdf_files],
            "upload_dir": self.upload_dir,
            "extraction_stats": self.processor.get_extraction_stats()
        }


def main():
    """Demo: Process sample PDFs"""
    print("\n" + "="*70)
    print("APACHE TIKA PDF DOCUMENT PROCESSOR")
    print("="*70)
    
    # Create sample PDF for testing
    pdf_dir = "data/sample_pdfs"
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Create a simple test document
    try:
        from reportlab.pdfgen import canvas
        pdf_path = os.path.join(pdf_dir, "sample_case.pdf")
        
        c = canvas.Canvas(pdf_path)
        c.drawString(100, 750, "JUDICIAL CASE SUMMARY")
        c.drawString(100, 700, "Case ID: CASE_001")
        c.drawString(100, 650, "Facts: Multiple witnesses testified that defendant committed the crime.")
        c.drawString(100, 600, "Verdict: GUILTY")
        c.drawString(100, 550, "Sentence: 5 years imprisonment")
        c.save()
        print(f"\n✓ Created sample PDF: {pdf_path}")
    except Exception as e:
        print(f"⚠ Could not create sample PDF: {e}")
    
    # Process PDFs
    processor = TikaDocumentProcessor()
    results = processor.process_pdf_directory(pdf_dir)
    
    print(f"\n[RESULTS] Processed {len(results)} PDFs")
    for result in results:
        if result["status"] == "success":
            print(f"  ✓ {result['filename']} ({result['extraction_method']})")
            print(f"    Text length: {result['text_length']} chars")
            print(f"    Pages: ~{result['pages']}")
    
    # Print statistics
    stats = processor.get_extraction_stats()
    print(f"\n[STATISTICS]")
    print(f"  Total: {stats['total_files']}")
    print(f"  Successful: {stats['successful']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Success Rate: {stats['success_rate']}%")
    print(f"  Methods used: {stats['extraction_methods']}")


if __name__ == "__main__":
    main()
