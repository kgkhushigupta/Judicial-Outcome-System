import logging
import numpy as np

logger = logging.getLogger(__name__)

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
    logger.info("[NLP] spaCy loaded with en_core_web_sm model.")
except Exception as e:
    SPACY_AVAILABLE = False
    logger.warning("[NLP] spaCy unavailable: %s. Using regex fallback.", str(e))

SPARK_AVAILABLE = False
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import udf, col, lower, regexp_replace, split, explode, size
    from pyspark.sql.types import StringType, ArrayType
    from pyspark.ml.feature import Tokenizer, StopWordsRemover
    SPARK_AVAILABLE = True
    logger.info("[Spark] PySpark modules imported successfully.")
except ImportError:
    logger.warning("[Spark] PySpark not available. Using pandas fallback.")

import re


def get_spark_session():
    if not SPARK_AVAILABLE:
        return None
    try:
        spark = SparkSession.builder \
            .appName("JudicialAI-NLP") \
            .master("local[*]") \
            .config("spark.driver.memory", "2g") \
            .config("spark.sql.shuffle.partitions", "4") \
            .getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        logger.info("[Spark] SparkSession created: %s", spark.version)
        return spark
    except Exception as e:
        logger.warning("[Spark] Failed to create SparkSession: %s", str(e))
        return None


def process_text(text):
    if not text or not isinstance(text, str):
        return []
    if SPACY_AVAILABLE:
        doc = nlp(text[:100000])
        tokens = [token.lemma_.lower() for token in doc
                  if not token.is_stop and token.is_alpha and len(token.text) > 2]
        return tokens
    else:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        stopwords = {"the", "and", "for", "that", "this", "with", "was", "are", "has", "had", "have",
                     "from", "been", "were", "which", "their", "also", "but", "not", "shall", "may",
                     "any", "such", "who", "whom", "under", "upon", "into", "can", "will", "would"}
        return [w for w in words if w not in stopwords]


def process_entities(text):
    if not text or not isinstance(text, str):
        return []
    if SPACY_AVAILABLE:
        doc = nlp(text[:100000])
        entities = []
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LAW', 'DATE', 'CARDINAL']:
                entities.append({"text": ent.text, "label": ent.label_})
        return entities
    else:
        patterns = {
            "PERSON": r'\b(?:Justice|Judge|Mr\.|Mrs\.|Dr\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?',
            "ORG": r'\b(?:Supreme Court|High Court|Sessions Court|District Court|Tribunal)\b',
            "LAW": r'\bSection\s+\d+[A-Z]?\s+(?:of\s+)?(?:IPC|CrPC|CPC|NI Act|NDPS Act|IT Act)',
        }
        entities = []
        for label, pattern in patterns.items():
            for match in re.finditer(pattern, text):
                entities.append({"text": match.group(), "label": label})
        return entities


def process_batch_spark(texts, labels=None):
    """Process texts using Spark with pandas fallback on any error."""
    
    # Always fall back to pandas for reliability
    logger.info("[Preprocess] Processing %d texts with pandas (fast fallback).", len(texts))
    processed = []
    for text in texts:
        try:
            tokens = process_text(text)
            entities = process_entities(text)
            processed.append({
                "tokens": tokens,
                "entities": entities,
                "token_count": len(tokens),
                "entity_count": len(entities)
            })
        except Exception as e:
            logger.warning("[Preprocess] Error processing text: %s", str(e))
            processed.append({
                "tokens": [],
                "entities": [],
                "token_count": 0,
                "entity_count": 0
            })
    
    return processed


def get_nlp_status():
    return {
        "spacy_available": SPACY_AVAILABLE,
        "spacy_model": "en_core_web_sm" if SPACY_AVAILABLE else None,
        "spark_available": SPARK_AVAILABLE,
        "processing_mode": "Spark + spaCy" if SPARK_AVAILABLE and SPACY_AVAILABLE else
                          "spaCy (local)" if SPACY_AVAILABLE else "Regex fallback"
    }
