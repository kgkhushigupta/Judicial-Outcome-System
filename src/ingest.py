import os
import logging

logger = logging.getLogger(__name__)

def extract_pdf_text(filepath):
    if not os.path.exists(filepath):
        logger.error("[Tika] File not found: %s", filepath)
        return ""
    try:
        from tika import parser
        raw = parser.from_file(filepath)
        content = raw.get("content", "")
        if content:
            text = content.strip()
            logger.info("[Tika] Extracted %d characters from %s", len(text), filepath)
            return text
        logger.warning("[Tika] No content extracted from %s", filepath)
        return ""
    except ImportError:
        logger.warning("[Tika] tika-python not installed. Attempting raw text read.")
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception as e:
        logger.error("[Tika] Extraction failed: %s", str(e))
        return ""

def ingest_uploaded_file(filepath, upload_dir="data/uploads"):
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return extract_pdf_text(filepath)
    elif ext in [".txt", ".text"]:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    else:
        logger.warning("[Ingest] Unsupported file type: %s", ext)
        return ""
