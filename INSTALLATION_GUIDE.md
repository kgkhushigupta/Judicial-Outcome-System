# Installation & Troubleshooting Guide

## Quick Start: Complete 10-Step Installation

```bash
# Step 1: Install all Python packages
pip install -r requirements.txt

# Step 2: Download spaCy model (Legal NLP)
python -m spacy download en_core_web_sm

# Step 3: Verify installations
python -c "import pyspark; import xgboost; import aif360; import fairlearn; print('✓ All packages installed')"

# Step 4: Test individual modules
cd Judicial-AI-System
python src/big_data_layer.py          # Test Big Data Processing
python src/embedding/case_embeddings.py  # Test Embeddings
python src/prediction/outcome_model.py   # Test XGBoost predictor
python src/bias_detection/bias_detector.py # Test Bias Detection

# Step 5: Run complete system validation
python validate_system.py

# Step 6: Run full demo pipeline
python run_demo.py

# Step 7-10: Review outputs
# - open output/report.html in browser (Visual dashboard)
# - check output/results.json (Structured results)
# - check output/predictions.csv (Predictions export)
# - check data/hdfs/ (HDFS structure)
```

---

## Technology Stack Detailed Installation

### 1. Apache Spark (Big Data Processing)
**Status**: ✓ Integrated in `big_data_layer.py`

#### Windows Installation:
```bash
# Install via pip (easiest)
pip install pyspark>=3.2.0

# Verify installation
python -c "from pyspark.sql import SparkSession; spark = SparkSession.builder.master('local').getOrCreate(); print('✓ Spark ready')"
```

**If Spark fails (most common):**

**Error**: `java.lang. OutOfMemoryError`
```bash
# Set environment variables
setx JAVA_OPTS "-Xms512m -Xmx1024m"

# Or use smaller memory in code:
from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .config("spark.driver.memory", "512m") \
    .config("spark.executor.memory", "256m") \
    .getOrCreate()
```

**Error**: `JAVA_HOME not set`
```bash
# 1. Install Java 8, 11, or 17
# https://www.oracle.com/java/technologies/downloads/

# 2. Set JAVA_HOME (Windows)
setx JAVA_HOME "C:\Program Files\Java\jdk-11.0.15"

# 3. Restart terminal

# 4. Verify
java -version
```

### 2. HDFS (Storage)
**Status**: ✓ HdfsSimulator working (demo mode)

For production HDFS cluster, config in `big_data_layer.py`:
```python
os.environ['HADOOP_HOME'] = '/opt/hadoop-3.2.0'
os.environ['HADOOP_CONF_DIR'] = '/opt/hadoop-3.2.0/etc/hadoop'
```

### 3. Apache Tika (PDF Ingestion)
**Status**: ✓ Integrated in `ingestion/pdf_extractor.py`

```bash
# Install Python client
pip install tika>=1.24

# Requires Java 8+ (already set for Spark)

# Test
python -c "from tika import parser; print('✓ Tika ready')"
```

**If Tika fails**: Falls back to PyPDF2 automatically (already in requirements)

### 4. spaCy + InLegalBERT (Legal NLP)
**Status**: ✓ Integrated in `nlp/` modules

```bash
# Install spaCy
pip install spacy>=3.0.0

# Download English model
python -m spacy download en_core_web_sm

# InLegalBERT (optional, auto-downloads)
# - Will download on first use via transformers cache
# - No manual installation needed

# Test
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✓ spaCy ready')"
```

### 5. Neo4j (Knowledge Graph)
**Status**: ✓ Integrated with offline mode fallback

```bash
# Install Python driver
pip install neo4j>=4.3.0

# Option A: Docker (easiest)
docker run -d -p 7687:7687 -p 7474:7474 neo4j:latest

# Option B: Download desktop
# https://neo4j.com/download/

# Test connection
python -c "from neo4j import GraphDatabase; print('✓ Neo4j driver ready')"
```

**If Neo4j unavailable**: Falls back to offline mode (JSON storage)

### 6. Sentence-Transformers + FAISS (Similarity Search)
**Status**: ✓ Integrated in `embeddings/` and `similarity/`

```bash
# Install both
pip install sentence-transformers>=2.2.0
pip install faiss-cpu>=1.7.0  # or faiss-gpu for GPU

# For GPU acceleration (optional)
pip install faiss-gpu

# Test
python -c "from sentence_transformers import SentenceTransformer; from faiss import IndexFlatL2; print('✓ Ready')"
```

### 7. XGBoost (Prediction)
**Status**: ✓ Integrated in `prediction/outcome_model.py`

```bash
# Install XGBoost
pip install xgboost>=1.5.0

# Test
python -c "import xgboost; print('✓ XGBoost ready')"
```

### 8. AIF360 + Fairlearn (Bias Detection)
**Status**: ✓ Integrated in `bias_detection/bias_detector.py`

```bash
# Install both libraries
pip install aif360>=0.4.0
pip install fairlearn>=0.7.0

# Test
python -c "import aif360; import fairlearn; print('✓ Bias tools ready')"
```

---

## Diagnostic Commands

### Check Installation Status
```bash
# Test each technology
python -c "
import pyspark
import xgboost
import sentence_transformers
import aif360
import fairlearn
import spacy
import neo4j
import faiss
print('✓ All core packages installed')
"

# Check specific versions
pip show pyspark xgboost sentence-transformers aif360 fairlearn
```

### Run Module-Specific Tests
```bash
# Big Data Layer
cd Judicial-AI-System
python src/big_data_layer.py
# Expected: Shows 8-partition processing, HDFS simulation

# PDF Extraction
python -c "
from src.ingestion.pdf_extractor import PDFExtractor
ext = PDFExtractor()
print('✓ PDF extractor ready')
"

# Embeddings with Sentence-Transformers
python -c "
from src.embeddings.case_embeddings import CaseEmbedder
emb = CaseEmbedder()
text = 'Case about fraud charges'
e = emb.embed_text(text)
print(f'✓ Embeddings ready (shape: {e.shape})')
"

# XGBoost Prediction
python -c "
from src.prediction.outcome_model import OutcomePredictor
pred = OutcomePredictor()
print('✓ XGBoost predictor ready')
"

# Bias Detection with AIF360
python -c "
from src.bias_detection.bias_detector import BiasDetector
bd = BiasDetector()
print('✓ Bias detector ready')
"

# Knowledge Graph
python -c "
from src.knowledge_graph.neo4j_loader import Neo4jLoader
neo = Neo4jLoader(offline_mode=True)
print('✓ Neo4j loader ready')
"
```

---

## Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Spark not found** | `java.lang.ClassNotFoundException` | Install Java: https://www.oracle.com/java/technologies/downloads/ |
| **OutOfMemory** | `java.lang.OutOfMemoryError` | Use `--driver-memory 512m --executor-memory 256m` or reduce dataset |
| **Tika fails** | `RuntimeError: Tika server is not running` | Falls back to PyPDF2 automatically |
| **FAISS build error** | `error: Microsoft Visual C++ build tools required` | Install: https://visualstudio.microsoft.com/visual-cpp-build-tools/ |
| **torch/transformers versions** | `ImportError: no module named torch` | `pip install --upgrade torch transformers` |
| **Neo4j connection timeout** | `neo4j.exceptions.BoltConnectionError` | Falls back to offline mode OR start Neo4j server |
| **GPU FAISS issues** | FAISS GPU build fails | Use CPU version: `pip install faiss-cpu` |
| **PDF extraction blank** | Empty text extracted | Ensure PDF has selectable text (not image-based) |

---

## Complete System Validation

Run the integrated validation script:

```bash
python validate_system.py
```

Expected output:
```
✓ Text Cleaning Works
✓ Keyword Extraction Works
✓ Entity Extraction Works
✓ Section Detection Works
✓ Embeddings Generated (Sentence-Transformers)
✓ FAISS Indexing Works
✓ Keyword Clustering Works
✓ Outcome Prediction Works (XGBoost)
✓ Bias Detection Works (AIF360+Fairlearn)
✓ Reasoning Engine Works
✓ Neo4j Integration Works (offline)
✓ Dataset Available
✓ Output Generation Works

ALL TESTS PASSED! ✓
```

---

## Full Pipeline Execution

```bash
python run_demo.py
```

Expected output:
```
[1/9] LOAD DATASET ✓
[2/9] TEXT PREPROCESSING (Distributed) ✓
[3/9] KEYWORD EXTRACTION ✓
[4/9] EMBEDDINGS (Sentence-Transformers) ✓
[5/9] FAISS INDEX ✓
[6/9] SIMILARITY SEARCH ✓
[7/9] PREDICTION (XGBoost) ✓
[8/9] BIAS DETECTION (AIF360) ✓
[9/9] EXPLANATIONS (Neo4j) ✓

Generated:
✓ output/report.html (16.7 KB)
✓ output/results.json (1.9 KB)
✓ output/predictions.csv (3.7 KB)
```

---

## Technology Matrix: What Gets Used Where

| Component | Technology | Module | Auto-Fallback |
|-----------|-----------|--------|---|
| Text Input | PDF reading | `ingestion/pdf_extractor.py` | PyPDF2 |
| Distributed Processing | Apache Spark | `big_data_layer.py` | Pandas partitions |
| Data Storage | HDFS | `big_data_layer.py` | Local filesystem |
| NLP | spaCy + InLegalBERT | `nlp/` | Basic tokenization |
| Embeddings | Sentence-Transformers | `embeddings/case_embeddings.py` | TF-IDF fallback |
| Vector Index | FAISS | `similarity/` | Numpy similarity |
| Prediction | XGBoost | `prediction/outcome_model.py` | RandomForest |
| Bias Analysis | AIF360 + Fairlearn | `bias_detection/` | Basic metrics |
| Knowledge Graph | Neo4j | `knowledge_graph/` | JSON offline mode |
| Reasoning | Graph Traversal | `explanation/reasoning_engine.py` | Template-based |

---

## Environment Setup (Optional but Recommended)

### Create Virtual Environment
```bash
# Python 3.9+ recommended
python -m venv judicial_env

# Activate
# Windows:
judicial_env\Scripts\activate
# Linux/Mac:
source judicial_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Spark Cluster Setup (Production)
```bash
# Configure for cluster deployment
SPARK_MASTER_HOST=cluster-master
SPARK_MASTER_PORT=7077

spark-submit \
  --master spark://$SPARK_MASTER_HOST:$SPARK_MASTER_PORT \
  --num-executors 64 \
  --executor-memory 4g \
  --driver-memory 2g \
  run_pipeline.py
```

---

## Verification Checklist

Before running demos, verify:

- [ ] `python -c "import pyspark; print(pyspark.__version__)"`  → 3.2.0+
- [ ] `python -c "import xgboost; print(xgboost.__version__)"`  → 1.5.0+
- [ ] `python -c "import aif360; print('✓')"` → ✓
- [ ] `python -c "import fairlearn; print('✓')"` → ✓
- [ ] `python -m spacy download en_core_web_sm` → Downloaded
- [ ] `java -version` → Java 8, 11, or 17 installed
- [ ] `python run_demo.py` → Completes without errors
- [ ] `ls output/report.html` → File exists and renders in browser

---

## Support Resources

- **Spark Issues**: https://spark.apache.org/docs/3.2.0/
- **XGBoost**: https://xgboost.readthedocs.io/
- **AIF360**: https://github.com/Trusted-AI/AIF360
- **Fairlearn**: https://fairlearn.org/
- **Sentence-Transformers**: https://www.sbert.net/
- **Neo4j**: https://neo4j.com/docs/

All issues with fallbacks - system won't crash! ✓
