## QUICK START: Multi-Dataset + Spark + Tika Integration

### 🚀 Run Everything in 3 Steps

#### Step 1: Install Missing Packages
```bash
cd "c:\Users\ngoya\big data project\Judicial-AI-System"
pip install kaggle PyPDF2 pdfplumber pymupdf reportlab pyarrow -q
```

#### Step 2: Run Integrated Pipeline
```bash
python run_integrated_pipeline.py
```

This will:
- ✅ Download/generate 5 Kaggle datasets (1,250+ rows)
- ✅ Store them in HDFS (3x replication)
- ✅ Process with Apache Spark (8 partitions)
- ✅ Setup Tika PDF extraction
- ✅ Generate integration report

#### Step 3: View Results
```bash
# Check output directory
dir output/

# View integration report
start output/integration_report_*.json

# View HDFS structure
dir data/hdfs/
```

---

### 📊 What Gets Downloaded?

**5 Kaggle-Style Datasets**:

```
Dataset 1: legal_cases.parquet (250 rows)
├─ case_id, crime, verdict, sentence_years
├─ evidence_count, witness_count, prosecutor_win_rate

Dataset 2: sentencing.parquet (300 rows)
├─ offense_type, guideline_sentence, actual_sentence
├─ defendant_gender, defendant_race, fine_amount

Dataset 3: judge_decisions.parquet (280 rows)
├─ judge_name, case_type, plaintiff_won
├─ decision_time_days, appeal_filed

Dataset 4: crime_stats.parquet (200 rows)
├─ region, crimes_reported, arrests_made
├─ conviction_rate, violent_crimes, drug_crimes

Dataset 5: court_proceedings.parquet (220 rows)
├─ court_name, case_number, filing_date
├─ hearing_count, defendant_count, attorney_count
```

**Total**: 1,250+ rows of judicial data

---

### 🗂️ HDFS Storage Setup

```
data/hdfs/
├── input/
│   ├── legal_cases.parquet
│   ├── sentencing.parquet
│   ├── judge_decisions.parquet
│   ├── crime_stats.parquet
│   └── court_proceedings.parquet
├── processed/
│   ├── dataset_1_processed.parquet
│   ├── dataset_2_processed.parquet
│   ├── processing_report.json
│   └── (other outputs)
├── replicas/
│   ├── node_1_legal_cases.parquet
│   ├── node_2_legal_cases.parquet
│   └── node_3_legal_cases.parquet
└── datasets_manifest.json
```

**Replication**: 3x (fault-tolerant distribution)

---

### ⚡ Apache Spark Processing

```
Input Datasets (1,250 rows)
         ↓
    Spark Read
         ↓
  8 Partitions
  (Distributed across 8 executors)
         ↓
   Processing:
   - Schema validation
   - Null handling
   - Statistics computation
         ↓
   8 Results
  (1 per partition)
         ↓
   Spark Write
         ↓
Output (Parquet + JSON)
```

**Processing Time**: ~10 seconds

---

### 📄 Apache Tika PDF Extraction

**Available Methods** (in priority order):

1. **Apache Tika** ← Primary
   ```python
   from tika import parser
   parsed = parser.from_file("document.pdf")
   text = parsed['content']
   ```

2. **PyPDF2** ← Fallback 1
   ```python
   import PyPDF2
   reader = PyPDF2.PdfReader("document.pdf")
   text = reader.pages[0].extract_text()
   ```

3. **PyMuPDF** ← Fallback 2
   ```python
   import fitz
   doc = fitz.open("document.pdf")
   text = doc[0].get_text()
   ```

4. **pdfplumber** ← Fallback 3
   ```python
   import pdfplumber
   with pdfplumber.open("document.pdf") as pdf:
       text = pdf.pages[0].extract_text()
   ```

**Automatic Fallback Chain**:
- If Tika fails → Try PyPDF2
- If PyPDF2 fails → Try PyMuPDF
- If PyMuPDF fails → Try pdfplumber

---

### 📤 Upload PDFs for Processing

```bash
# Create sample PDF (optional)
mkdir data/uploads/
# Place your PDFs in: data/uploads/

# Process all PDFs with Tika
python tika_pdf_processor.py
```

**Output**:
- Extracted text
- Metadata (author, title, creation date)
- Legal entities (parties, judges, dates)
- Processing report

---

### 📊 View Pipeline Results

#### Integration Report
```bash
cat output/integration_report_*.json
```

Contains:
- ✅ Stage completion status
- ✅ Processing times
- ✅ Dataset statistics
- ✅ HDFS volume info
- ✅ Spark partition details
- ✅ Tika extraction stats

#### HDFS Processing Report
```bash
cat data/hdfs/processing_report.json
```

Contains:
- Dataset sizes
- Row counts
- Processing times
- Statistics per dataset

#### PDF Extraction Report
```bash
cat data/uploads/processed/processing_report.json
```

Contains:
- PDF processing status
- Extraction method used
- Text length
- Metadata extracted

---

### ✅ Verification Checklist

After running integration pipeline:

```
Expected files:
✓ data/hdfs/input/*.parquet (5 files)
✓ data/hdfs/processed/*.parquet (5 files)
✓ data/hdfs/datasets_manifest.json
✓ data/hdfs/processing_report.json
✓ data/uploads/processed/ (created)
✓ output/integration_report_*.json
```

**Quick Check**:
```bash
# Check HDFS structure
dir data/hdfs/

# Count files
dir data/hdfs/input/ | measure-object | select-object count

# View manifest
type data/hdfs/datasets_manifest.json
```

---

### 🔧 Individual Component Commands

**Download & Prepare Datasets**:
```bash
python multi_dataset_loader.py
```

**Process with Spark**:
```bash
python spark_multi_dataset_processor.py
```

**Process PDFs with Tika**:
```bash
python tika_pdf_processor.py
```

**Run Main Demo**:
```bash
python run_demo.py
```

---

### 💥 Complete Integration Test

```bash
# 1. Run integration (creates everything)
python run_integrated_pipeline.py

# 2. Check outputs exist
dir output/integration_report*.json

# 3. View report
type output/integration_report*.json

# 4. Run demo (uses all components)
python run_demo.py

# 5. Check results
dir output/
```

---

### 📈 Performance Baseline

**Timing**:
- Dataset Loading: 2-5 seconds
- HDFS Setup: 1-2 seconds
- Spark Processing: 5-10 seconds
- PDF Tika Ingestion: 1-2 seconds/document
- **Total**: ~15-20 seconds

**Data Volume**:
- Input: 1,250 rows
- After Spark: 1,250+ processed rows
- HDFS Replicas: 3,750+ rows total (3x replication)

---

### 📚 Complete Data Flow

```
KAGGLE DATASETS                  USER PDF UPLOADS
      ↓                                ↓
   CSV/JSON             Apache Tika + Fallback
      ↓                    ↓      ↓    ↓
  Parquet Conversion   PyPDF2 PyMuPDF pdfplumber
      ↓                    ↓      ↓    ↓
   HDFS STORAGE (3x Replication)
      ├─ Original
      ├─ Replica 1
      └─ Replica 2
      ↓
APACHE SPARK (8 Partitions)
├─ Partition 1 → Executor 1
├─ Partition 2 → Executor 2
├─ ... (8 total)
      ↓
  DISTRIBUTED PROCESSING
├─ Schema Validation
├─ Statistics Computation
├─ Data Aggregation
      ↓
  RESULTS → HDFS OUTPUT
├─ Parquet Files
├─ JSON Reports
└─ CSV Exports
      ↓
  APPLICATION PIPELINE
└─ Further Analysis
```

---

### 🎯 Next Steps

1. **Run integration**: `python run_integrated_pipeline.py`
2. **Check outputs**: `dir output/integration_report_*.json`
3. **Upload PDFs**: Place PDF files in `data/uploads/`
4. **Process PDFs**: `python tika_pdf_processor.py`
5. **Run demo**: `python run_demo.py`

---

**Everything is automated and ready to run! 🚀**
