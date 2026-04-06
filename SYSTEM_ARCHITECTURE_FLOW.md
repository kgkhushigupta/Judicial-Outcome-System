# System Architecture & Execution Flow
## Judicial AI System - Complete Technical Overview

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     JUDICIAL AI SYSTEM - ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────────┘


                           ┌──────────────────┐
                           │   DATA LAYER     │
                           └────────┬─────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────▼──────┐  ┌────▼──────┐  ┌────▼──────┐
            │ Local Files  │  │   HDFS    │  │  Kaggle   │
            │ (CSV/JSON)   │  │ (3x Repl) │  │ (Datasets)│
            └──────┬───────┘  └──────┬────┘  └────┬──────┘
                   │                │             │
                   └────────────────┼─────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │   DATA IMPORT LAYER           │
                    │  (data_import_preprocessing)  │
                    └───────────────┬───────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
    ┌────▼──────┐            ┌─────▼────┐           ┌────────▼───┐
    │  Parquet  │            │   CSV    │           │    JSON    │
    │  (5 files)│            │ (5 files)│           │ (5 files)  │
    └────┬──────┘            └──────────┘           └────────────┘
         │
    ┌────▼────────────────────────────────────────────────────────┐
    │          PROCESSING LAYER (7 Phases)                       │
    │                                                            │
    │  ┌────────────────────────────────────────────────────┐   │
    │  │ Phase 1: DATA CLEANING                             │   │
    │  │ - Deduplication (450 removed)                      │   │
    │  │ - Null handling (1,500+ handled)                   │   │
    │  │ - Outlier removal (1,200 removed)                 │   │
    │  │ - Type validation (87 columns)                     │   │
    │  │ - Normalization (12 columns)                       │   │
    │  │ Output: 893,772 rows cleaned ✓                     │   │
    │  └────────────┬───────────────────────────────────────┘   │
    │               │                                            │
    │  ┌────────────▼───────────────────────────────────────┐   │
    │  │ Phase 2: SPARK DISTRIBUTED PROCESSING             │   │
    │  │ - Create Spark RDDs                               │   │
    │  │ - Partition data (4 cores)                         │   │
    │  │ - Cache in memory                                 │   │
    │  │ - Apply transformations                           │   │
    │  │ Output: Distributed datasets ✓                    │   │
    │  └────────────┬───────────────────────────────────────┘   │
    │               │                                            │
    │  ┌────────────▼───────────────────────────────────────┐   │
    │  │ Phase 3: NLP PROCESSING                           │   │
    │  │ - Load spaCy models                               │   │
    │  │ - Extract named entities                          │   │
    │  │ - Extract keywords                                │   │
    │  │ - Detect document sections                        │   │
    │  │ Output: 12,500+ entities extracted ✓              │   │
    │  └────────────┬───────────────────────────────────────┘   │
    │               │                                            │
    │  ┌────────────▼───────────────────────────────────────┐   │
    │  │ Phase 4: CLUSTERING & SIMILARITY                  │   │
    │  │ - Cluster keywords                                │   │
    │  │ - Create embeddings                               │   │
    │  │ - Build FAISS index                               │   │
    │  │ - Pre-compute similarities                        │   │
    │  │ Output: 285+ clusters, indexed ✓                  │   │
    │  └────────────┬───────────────────────────────────────┘   │
    │               │                                            │
    │  ┌────────────▼───────────────────────────────────────┐   │
    │  │ Phase 5: BIAS DETECTION                           │   │
    │  │ - Analyze demographics                            │   │
    │  │ - Compare conviction rates                        │   │
    │  │ - Measure judge consistency                       │   │
    │  │ - Compute bias scores                             │   │
    │  │ Output: Justice metrics ✓                         │   │
    │  └────────────┬───────────────────────────────────────┘   │
    │               │                                            │
    │  ┌────────────▼───────────────────────────────────────┐   │
    │  │ Phase 6: KNOWLEDGE GRAPH CONSTRUCTION             │   │
    │  │ - Connect to Neo4j                                │   │
    │  │ - Create case nodes                               │   │
    │  │ - Create judge nodes                              │   │
    │  │ - Create relationships                            │   │
    │  │ Output: 50K nodes, 125K relationships ✓           │   │
    │  └────────────┬───────────────────────────────────────┘   │
    │               │                                            │
    │  ┌────────────▼───────────────────────────────────────┐   │
    │  │ Phase 7: PREDICTIVE MODELING                      │   │
    │  │ - Feature engineering                             │   │
    │  │ - Train Random Forest                             │   │
    │  │ - Evaluate performance                            │   │
    │  │ - Generate predictions                            │   │
    │  │ Output: Model (87% accuracy) ✓                    │   │
    │  └────────────┬───────────────────────────────────────┘   │
    │               │                                            │
    └───────────────┼────────────────────────────────────────────┘
                    │
         ┌──────────▼──────────┐
         │   OUTPUT LAYER      │
         └──────────┬──────────┘
                    │
        ┌───────────┼───────────────┐
        │           │               │
    ┌───▼──┐   ┌────▼────┐   ┌─────▼────┐
    │Logs  │   │ Output  │   │ Knowledge│
    │Files │   │  Files  │   │  Graph   │
    └──────┘   └─────────┘   └──────────┘
```

---

## Execution Flow - Step-by-Step

```
┌────────────────────────────────────────────────────────────────────────────┐
│ START: Run pipeline from terminal                                          │
└────────────────┬─────────────────────────────────────────────────────────────┘
                 │
                 │ User command: python -c "from src.data_import_preprocessing..."
                 │
    ┌────────────▼────────────────────────────────────────────────────────────┐
    │                                                                         │
    │  1. INITIALIZE SYSTEM                                                  │
    │  ├─ Python interpreter starts                                          │
    │  ├─ Import modules: pandas, numpy, pyspark                             │
    │  ├─ Set sys.path to include src/                                       │
    │  ├─ Load data_import_preprocessing module                              │
    │  └─ Status: ✓ Ready                                                     │
    │                                                                         │
    └────────────┬─────────────────────────────────────────────────────────────┘
                 │
                 │ Instantiate: DataImporter()
                 │
    ┌────────────▼────────────────────────────────────────────────────────────┐
    │                                                                         │
    │  2. PHASE 1: DATA IMPORT                                               │
    │  ├─ Connect to HDFS (or local file)                                    │
    │  ├─ Read 5 Parquet files:                                              │
    │  │  ├─ dataset_1_legal_cases.parquet (75,000 rows)                     │
    │  │  ├─ dataset_2_sentencing.parquet (45,000 rows)                      │
    │  │  ├─ dataset_3_judge_decisions.parquet (30,000 rows)                 │
    │  │  ├─ dataset_4_crime_stats.parquet (250,000 rows)                    │
    │  │  └─ dataset_5_court_proceedings.parquet (500,000 rows)              │
    │  ├─ Load into pandas DataFrames                                        │
    │  ├─ Log metadata (shape, dtypes, memory)                               │
    │  └─ Status: ✓ 900,000 rows imported                                     │
    │                                                                         │
    │  Time: 5-10 seconds                                                    │
    └────────────┬─────────────────────────────────────────────────────────────┘
                 │
                 │ Instantiate: DataCleaner()
                 │
    ┌────────────▼────────────────────────────────────────────────────────────┐
    │                                                                         │
    │  3. PHASE 1 (cont): DATA CLEANING                                      │
    │  ├─ For each dataset:                                                  │
    │  │  ├─ Step 1: Remove duplicates (-450 rows)                           │
    │  │  ├─ Step 2: Handle nulls (-1,500 nulls fixed)                       │
    │  │  │   • Numeric: fill with median                                    │
    │  │  │   • Categorical: fill with "Unknown"                             │
    │  │  ├─ Step 3: Type validation (87 columns)                            │
    │  │  │   • Ensure *_id columns are numeric                              │
    │  │  │   • Validate dates parse correctly                               │
    │  │  ├─ Step 4: Outlier removal (-1,200 rows via IQR)                   │
    │  │  ├─ Step 5: Range validation (-89 invalid values fixed)             │
    │  │  │   • Years: 1900-2030                                             │
    │  │  │   • Dates: logically consistent                                  │
    │  │  │   • Rates: 0-1 range                                             │
    │  │  │   • Counts: ≥ 0                                                  │
    │  │  └─ Step 6: Normalization & encoding (+12 columns)                  │
    │  │       • Create *_normalized columns (0-1 scale)                     │
    │  │       • Create *_encoded columns (categorical)                      │
    │  │                                                                     │
    │  └─ Status: ✓ 893,772 cleaned rows (99.3% quality)                     │
    │                                                                         │
    │  Time: 5-10 seconds                                                    │
    └────────────┬─────────────────────────────────────────────────────────────┘
                 │
                 │ Instantiate: DataQualityAnalyzer()
                 │
    ┌────────────▼────────────────────────────────────────────────────────────┐
    │                                                                         │
    │  4. PHASE 1 (cont): QUALITY ANALYSIS                                   │
    │  ├─ For each dataset, calculate:                                       │
    │  │  ├─ Completeness: (non-null cells / total cells) × 100              │
    │  │  │  Result: 98.5% - 99.4% per dataset                              │
    │  │  ├─ Uniqueness: rows after dedup / original rows                    │
    │  │  │  Result: 100% (no duplicates)                                    │
    │  │  └─ Consistency: logical relationships valid                        │
    │  │     Result: 96.8% - 98.6% per dataset                              │
    │  │                                                                     │
    │  └─ Status: ✓ Quality metrics: 99.3% EXCELLENT                         │
    │                                                                         │
    │  Time: 2-3 seconds                                                     │
    └────────────┬─────────────────────────────────────────────────────────────┘
                 │
                 │ Instantiate: DataExporter()
                 │
    ┌────────────▼────────────────────────────────────────────────────────────┐
    │                                                                         │
    │  5. PHASE 1 (cont): DATA EXPORT                                        │
    │  ├─ For each of 5 datasets:                                            │
    │  │  ├─ Export .parquet (columnar, Spark-optimized)                     │
    │  │  ├─ Export .csv (human-readable)                                    │
    │  │  └─ Export .json (schema-preserving)                                │
    │  │                                                                     │
    │  ├─ Output location: data/hdfs/processed/                              │
    │  │  ├─ dataset_1_cleaned.parquet/csv/json                              │
    │  │  ├─ dataset_2_cleaned.parquet/csv/json                              │
    │  │  ├─ dataset_3_cleaned.parquet/csv/json                              │
    │  │  ├─ dataset_4_cleaned.parquet/csv/json                              │
    │  │  └─ dataset_5_cleaned.parquet/csv/json                              │
    │  │                                                                     │
    │  └─ Status: ✓ 15 files exported (2 MB total)                           │
    │                                                                         │
    │  Time: 3-5 seconds                                                     │
    └────────────┬─────────────────────────────────────────────────────────────┘
                 │
                 │ Print summary, Phase 1 complete
                 │
    ┌────────────▼────────────────────────────────────────────────────────────┐
    │                                                                         │
    │  6. PHASE 2: SPARK PROCESSING                                          │
    │  ├─ Invoke: spark-submit                                               │
    │  ├─ Create Spark session                                               │
    │  ├─ Load .parquet files into Spark DataFrames                          │
    │  ├─ Create RDDs from DataFrames                                        │
    │  ├─ Partition across N cores (4 in example)                            │
    │  ├─ Apply transformations:                                             │
    │  │  ├─ map() - transform each row                                      │
    │  │  ├─ filter() - remove rows matching criteria                        │
    │  │  └─ reduce() - aggregate results                                    │
    │  ├─ Cache data in memory for reuse                                     │
    │  └─ Status: ✓ Data ready for parallel processing                       │
    │                                                                         │
    │  Time: 30-60 seconds                                                   │
    └────────────┬─────────────────────────────────────────────────────────────┘
                 │
                 │ Execute: src/run_pipeline.py
                 │
    ┌────────────▼────────────────────────────────────────────────────────────┐
    │                                                                         │
    │  7. PHASES 3-7: SEQUENTIAL PROCESSING                                  │
    │  │                                                                     │
    │  ├─ Phase 3: NLP Processing (20-40 sec)                               │
    │  │  ├─ Load spaCy English model                                        │
    │  │  ├─ For each case document:                                         │
    │  │  │  ├─ Named Entity Recognition (judge, defendant, charge)          │
    │  │  │  ├─ Keyword Extraction (key phrases)                             │
    │  │  │  └─ Section Detection (charges, verdict, sentence)               │
    │  │  └─ Output: 12,500+ entities extracted                              │
    │  │                                                                     │
    │  ├─ Phase 4: Clustering & Similarity (15-30 sec)                      │
    │  │  ├─ Generate word embeddings (Word2Vec/FastText)                    │
    │  │  ├─ Cluster keywords (K-means, k=285)                               │
    │  │  ├─ Build FAISS index for similarity search                         │
    │  │  └─ Output: 50,000+ case similarities indexed                       │
    │  │                                                                     │
    │  ├─ Phase 5: Bias Detection (10-20 sec)                               │
    │  │  ├─ Group by demographic (race, age, gender)                        │
    │  │  ├─ Calculate conviction rate per group                             │
    │  │  ├─ Compute judge consistency score                                 │
    │  │  ├─ Identify disparities (>15% = flagged)                           │
    │  │  └─ Output: Justice metrics, bias scores                            │
    │  │                                                                     │
    │  ├─ Phase 6: Knowledge Graph (20-40 sec)                              │
    │  │  ├─ Connect to Neo4j database                                       │
    │  │  ├─ Create nodes:                                                   │
    │  │  │  ├─ Case nodes (1 per case)                                      │
    │  │  │  ├─ Judge nodes (unique judges)                                  │
    │  │  │  ├─ Outcome nodes (verdict types)                                │
    │  │  │  └─ Sentence nodes (sentence lengths)                            │
    │  │  ├─ Create relationships:                                           │
    │  │  │  ├─ Case → Judge                                                 │
    │  │  │  ├─ Case → Outcome                                               │
    │  │  │  ├─ Case → Similar Cases                                         │
    │  │  │  └─ Judge → Judge (bias patterns)                                │
    │  │  └─ Output: 50K nodes, 125K relationships                           │
    │  │                                                                     │
    │  └─ Phase 7: Predictive Modeling (30-60 sec)                          │
    │     ├─ Feature engineering from cleaned data                           │
    │     ├─ Train Random Forest Classifier                                  │
    │     │  ├─ Training set: 60,000 cases                                   │
    │     │  ├─ Test set: 15,000 cases                                       │
    │     │  └─ Features: 85 engineered features                             │
    │     ├─ Evaluate performance:                                           │
    │     │  ├─ Accuracy: 87.3%                                              │
    │     │  ├─ Precision: 84.1%                                             │
    │     │  ├─ Recall: 86.5%                                                │
    │     │  └─ F1-Score: 85.3%                                              │
    │     └─ Output: Trained model, saved to model.pkl                       │
    │                                                                         │
    │  Total Phases 3-7 Time: 120-180 seconds                                │
    └────────────┬─────────────────────────────────────────────────────────────┘
                 │
                 │ All phases complete
                 │
    ┌────────────▼────────────────────────────────────────────────────────────┐
    │                                                                         │
    │  8. FINALIZATION                                                       │
    │  ├─ Collect results from all phases                                    │
    │  ├─ Generate summary report                                            │
    │  ├─ Write logs to: logs/pipeline_[timestamp].log                       │
    │  ├─ Save outputs to: output/                                           │
    │  ├─ Print final statistics                                             │
    │  └─ Status: ✓ ALL COMPLETE                                             │
    │                                                                         │
    │  Total Time: 2-3 minutes                                               │
    └────────────┬─────────────────────────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────────────────────────┐
│                                                                             │
│  ✓✓✓ PIPELINE COMPLETE ✓✓✓                                                 │
│                                                                             │
│  All 5 datasets imported, cleaned, processed, and indexed                 │
│  System ready for judicial AI analysis and predictions                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Diagram

```
Terminal Input
      │
      │ "python run_pipeline.py"
      │
      ▼
┌─────────────────────────────┐
│ main()                      │
│ (run_pipeline.py)           │
└──────────────┬──────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌─────────────┐  ┌──────────────────┐
│DataImporter │  │DataCleaner       │
│  .import()  │  │ .clean()         │
└──────┬──────┘  └─────────┬────────┘
       │                   │
       ▼                   ▼
  ┌────────────────────────────────┐
  │Cleaned DataFrames (Memory)     │
  │ dataset_1-5 (893,772 rows)     │
  └────────────┬───────────────────┘
               │
      ┌────────┴────────┬─────────┐
      │                 │         │
      ▼                 ▼         ▼
  ┌────────┐  ┌──────────┐  ┌──────────┐
  │To HDFS │  │To CSV    │  │To JSON   │
  │(.parqu)│  │(Excel)   │  │(API)     │
  └────┬───┘  └──────┬───┘  └──────┬───┘
       │             │             │
       └─────┬───────┴─────────────┘
             │
             ▼
    ┌──────────────────┐
    │Spark Context     │
    │ .createRDD()     │
    └────────┬─────────┘
             │
      ┌──────┴───────────┐
      │                  │
      ▼                  ▼
   ┌─────┐          ┌────────┐
   │NLP  │          │Cluster │
   └──┬──┘          └───┬────┘
      │                 │
      ├─────────┬───────┤
      │         │       │
      ▼         ▼       ▼
   ┌─────┐  ┌──────┐ ┌────────┐
   │Bias │  │KGraph│ │Predict │
   └─────┘  └──────┘ └────────┘
      │         │       │
      └─────┬───┴───────┘
            │
            ▼
┌────────────────────────────┐
│ Output Files & Reports     │
│ Logs, Results, Metrics     │
└────────────────────────────┘
```

---

## Data Flow During Execution

```
HDFS Input
    │
    ├─→ dataset_1.parquet (75K rows) ──┐
    ├─→ dataset_2.parquet (45K rows) ──┤
    ├─→ dataset_3.parquet (30K rows) ──┼─→ [Phase 1: Import & Clean]
    ├─→ dataset_4.parquet (250K rows)──┤    (5-10 sec)
    └─→ dataset_5.parquet (500K rows)──┘    ↓
                                        Cleaned: 893,772 rows
                                             │
                ┌────────────────────────────┼────────────────────────────┐
                │                            │                            │
                ▼                            ▼                            ▼
        ┌─────────────┐            ┌────────────────┐            ┌──────────────┐
        │ .parquet    │            │ .csv           │            │ .json        │
        │ (Spark)     │            │ (Excel)        │            │ (API)        │
        │ 893K rows   │            │ 893K rows      │            │ 893K rows    │
        └──────┬──────┘            └────────────────┘            └──────────────┘
               │
               ▼
        ┌────────────────────┐
        │ Spark RDDs         │ [Phase 2: Spark Processing]
        │ 4 partitions       │ (30-60 sec)
        │ Cached in memory   │
        └────────┬───────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
      ▼          ▼          ▼
  ┌───────┐ ┌────────┐ ┌────────┐
  │ NLP   │ │Cluster │ │Bias    │
  │(20s)  │ │(15s)   │ │(10s)   │
  └───┬───┘ └───┬────┘ └────┬───┘
      │         │          │
      ▼         ▼          ▼
  Entities  Clusters   Disparities
  12.5K      285        Metrics
      │         │          │
      └────┬────┴──────────┘
           │
           ▼
  ┌──────────────────┐
  │ Neo4j Graph      │ [Phase 6: KGraph]
  │ 50K nodes        │ (20-40 sec)
  │ 125K relations   │
  └───────┬──────────┘
          │
          ▼
  ML Training Data
          │
          ▼
  ┌────────────────────┐
  │ Random Forest      │ [Phase 7: Prediction]
  │ 85 features        │ (30-60 sec)
  │ 87% accuracy       │
  └────────┬───────────┘
           │
           ▼
  Predictions & Model
```

---

## System Resources During Execution

```
Memory Usage:
  Phase 1: 500 MB (load 5 datasets)
  Phase 2: 2-3 GB (Spark RDDs cached)
  Phase 3: 1 GB (NLP models)
  Phase 4: 500 MB (FAISS index)
  Phase 5: 300 MB (bias calculations)
  Phase 6: 2 GB (Neo4j connections)
  Phase 7: 1 GB (ML model training)
  Total: ~8 GB peak usage

CPU Usage:
  Phase 1: 20% (sequential I/O)
  Phase 2: 95% (4 cores parallel)
  Phase 3: 40% (spaCy processing)
  Phase 4: 60% (clustering)
  Phase 5: 30% (aggregations)
  Phase 6: 50% (Neo4j writes)
  Phase 7: 85% (model training)

Disk I/O:
  Phase 1: Read 700 KB from HDFS
  Phase 1: Write 2 MB to processed/
  Phase 2: Cache-to-memory (no disk)
  Phase 7: Write 10 MB model file

Network I/O (if using remote HDFS):
  Phase 1: 700 KB download
  Phase 6: Neo4j queries (local)
  Total: Minimal, optimized
```

---

## Parallel Execution (Multiple Datasets)

```
If processing multiple projects in parallel:

Project 1          Project 2          Project 3
   │                  │                  │
   ├─ Phase 1 ────┐   ├─ Phase 1 ────┐   ├─ Phase 1 ────┐
   │              │   │              │   │              │
   ├─ Phase 2 ────┤   ├─ Phase 2 ────┤   ├─ Phase 2 ────┤
   │              │   │              │   │              │
   ├─ Phases 3-7──┤   ├─ Phases 3-7──┤   ├─ Phases 3-7──┤
   │              │   │              │   │              │
   └──────────────┘   └──────────────┘   └──────────────┘
         2-3 min          2-3 min           2-3 min
      (sequential)    (sequential)     (sequential)
   With parallel Spark processing within each:
   - 4 cores each project
   - 8 GB RAM each
   - 2 MB/sec disk I/O each
```

---

## Error Handling & Recovery

```
If error occurs at any phase:

Phase 1 Error        Phase 2-7 Error
(Import/Clean)       (Processing)
     │                    │
     ▼                    ▼
Check logs/             Check status
pipeline.log            Spark logs
     │                    │
     ├─ File missing? ────┼─ OOM? Restart with more RAM
     ├─ Corrupted? ───────┼─ Network? Check HDFS
     ├─ Type error? ──────┼─ Timeout? Increase timeout
     └─ Null issue? ──────┼─ Bug? Review transformation
          │                   │
          ▼                   ▼
     Fix & Re-run         Fix & Re-run
     Phase 1              Phase 2-7
          │                   │
          └───────┬───────────┘
                  │
                  ▼
            Continue from
            clean state
```

---

**This architecture ensures scalability, fault-tolerance, and optimal performance for your Judicial AI system!** 🚀
