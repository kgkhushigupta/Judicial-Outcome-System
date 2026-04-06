# Data Import & Preprocessing Documentation
## Judicial AI System - Complete Data Flow

---

## Overview: 5-Dataset Pipeline

```
HDFS INPUT DATA
    ↓
[IMPORT] Load from Parquet files
    ↓
[CLEAN] Remove duplicates, null values, outliers
    ↓
[VALIDATE] Type checking, range validation
    ↓
[ANALYZE] Quality metrics measurement
    ↓
[EXPORT] Save to Parquet/CSV/JSON
    ↓
HDFS OUTPUT DATA (Ready for Processing)
```

---

## The 5 Datasets

### 1. **Legal Cases Dataset** (`dataset_1`)
**Purpose:** Contains case metadata and details

**Fields Example:**
```
- case_id (int)              # Unique identifier
- case_name (string)         # Case title
- filing_date (date)         # When case was filed
- plaintiff (string)         # Party A
- defendant (string)         # Party B
- jurisdiction (string)      # Court location
- case_status (string)       # Open/Closed/Pending
- case_type (string)         # Criminal/Civil
- case_value (float)         # Monetary value if applicable
```

**Cleaning Steps:**
- Remove duplicate cases (same case_id)
- Handle null filing_dates → use median date
- Validate dates are between 1900-2030
- Standardize jurisdiction names
- Remove rows where case_type is invalid

**Size:** ~50,000-100,000 rows
**Columns:** 15-20
**Primary Key:** case_id


### 2. **Sentencing Dataset** (`dataset_2`)
**Purpose:** Criminal sentencing outcomes and penalties

**Fields Example:**
```
- sentencing_id (int)        # Unique identifier
- case_id (int)              # FK to legal_cases
- sentence_length (int)      # Months
- sentence_type (string)     # Prison/Fine/Probation/Community Service
- offense_severity (string)  # Felony/Misdemeanor
- judge_id (int)             # FK to judge_decisions
- sentence_date (date)       # When sentencing occurred
- defendant_age (int)        # At time of sentencing
- prior_convictions (int)    # Count
- recidivism_flag (bool)     # Whether reoffended
```

**Cleaning Steps:**
- Remove duplicates by sentencing_id
- Handle null sentence_lengths → 0 (no sentence)
- Validate sentence_length > 0 if sentence_type is Prison
- Check defendant_age is reasonable (18-100)
- Remove outliers in sentence_length (IQR method)
- Validate recidivism_flag is binary

**Size:** ~30,000-60,000 rows
**Columns:** 12-18
**Primary Key:** sentencing_id
**Foreign Keys:** case_id, judge_id


### 3. **Judge Decisions Dataset** (`dataset_3`)
**Purpose:** Judicial decision patterns and rulings

**Fields Example:**
```
- decision_id (int)          # Unique identifier
- judge_id (int)             # Which judge
- judge_name (string)        # Judge's name
- decision_type (string)     # Guilty/Not Guilty/Acquittal/Mistrial
- decision_confidence (float) # 0-1 confidence score
- case_id (int)              # FK to legal_cases
- decision_date (date)       # When decision made
- case_complexity (int)      # 1-10 scale
- legal_precedent (bool)     # Any precedent citations
- appeal_filed (bool)        # Was appealed
- appeal_successful (bool)   # If appealed, was it successful
```

**Cleaning Steps:**
- Remove duplicates by decision_id
- Validate decision_confidence is 0-1 range
- Categorical validation for decision_type
- Handle null legal_precedent as False
- Validate case_complexity is 1-10
- Ensure appeal_successful is null if appeal_filed is False

**Size:** ~25,000-50,000 rows
**Columns:** 14-20
**Primary Key:** decision_id
**Foreign Keys:** judge_id, case_id


### 4. **Crime Statistics Dataset** (`dataset_4`)
**Purpose:** Aggregated crime data by jurisdiction/category

**Fields Example:**
```
- stat_id (int)              # Unique identifier
- year (int)                 # Year of statistic
- jurisdiction (string)      # Geographic area
- crime_category (string)    # Type of crime
- offense_count (int)        # How many offenses
- arrest_count (int)         # How many arrests
- conviction_count (int)     # How many convictions
- victim_count (int)         # How many victims
- crime_rate (float)         # Per 100,000 population
- solved_rate (float)        # % solved (0-1)
- demographic_category (string) # Age/Gender/Race
```

**Cleaning Steps:**
- Remove duplicates by (year, jurisdiction, crime_category, demographic_category)
- Validate year is 1990-2030
- Null handling: offense_count → 0
- Validate counts: offense_count >= arrest_count >= conviction_count
- Validate rates are 0-1 range
- Check victim_count <= offense_count
- Standardize jurisdiction names
- Fix inconsistent demographic categories

**Size:** ~100,000-500,000 rows (aggregated, not row-level)
**Columns:** 12-15
**Primary Key:** (year, jurisdiction, crime_category, demographic_category)


### 5. **Court Proceedings Dataset** (`dataset_5`)
**Purpose:** Detailed court hearing and proceeding logs

**Fields Example:**
```
- proceeding_id (int)        # Unique identifier
- case_id (int)              # FK to legal_cases
- judge_id (int)             # FK to judge_decisions
- proceeding_date (date)     # When proceeding occurred
- proceeding_type (string)   # Hearing/Trial/Preliminary/Motion
- duration_minutes (int)     # How long it lasted
- attendees_count (int)      # How many people attended
- outcome (string)           # Outcome of proceeding
- notes (string)             # Proceeding notes (text)
- docket_number (string)     # Court docket ID
- scheduled_vs_actual_mismatch (bool) # If scheduled date ≠ actual
- courtroom_id (string)      # Which courtroom
```

**Cleaning Steps:**
- Remove duplicates by proceeding_id
- Validate proceeding_date is reasonable
- Check duration_minutes > 0 and < 480 (8 hours)
- Validate attendees_count > 0
- Categorical validation for proceeding_type and outcome
- Null handling: notes → "No notes recorded"
- Remove if critical fields null
- Validate proceeding_date >= associated case filing_date

**Size:** ~200,000-1,000,000 rows
**Columns:** 13-16
**Primary Key:** proceeding_id
**Foreign Keys:** case_id, judge_id


---

## Data Import Flow (Step 1)

```python
# HDFS Input Structure:
data/
└── hdfs/
    └── input/
        ├── legal_cases.parquet            (50KB-100KB)
        ├── sentencing.parquet              (30KB-60KB)
        ├── judge_decisions.parquet         (25KB-50KB)
        ├── crime_stats.parquet             (100KB-500KB)
        └── court_proceedings.parquet       (200KB-1000KB)

# Import Process:
for each dataset:
    1. Read Parquet from HDFS
    2. Load into Pandas DataFrame
    3. Store in memory
    4. Log: shape, dtypes, memory usage
    5. Check for missing files
```

### Import Output:
```
✓ dataset_1: legal_cases.parquet
  - Shape: 75,000 rows × 18 columns
  - Size: 85.50 KB
  - Columns: case_id, case_name, filing_date...
  - Data types: {'case_id': int64, 'case_name': object, ...}

✓ dataset_2: sentencing.parquet
  - Shape: 45,000 rows × 15 columns
  - Size: 42.30 KB
  ...
```

---

## Data Cleaning Flow (Step 2)

### Cleaning Pipeline for Each Dataset:

```
[Original Data]
    ↓
1. DEDUPLICATION
   - Remove exact duplicate rows
   - Report: X duplicates removed
    ↓
2. NULL VALUE HANDLING
   - Numeric columns: Fill with median
   - Text columns: Fill with "Unknown"
   - Date columns: Fill with most recent valid date
   - Report: X nulls handled
    ↓
3. TYPE CONVERSION & VALIDATION
   - Ensure *_id columns are numeric
   - Ensure *_count columns are numeric
   - Ensure dates parse correctly
   - Report: Y type conversions applied
    ↓
4. OUTLIER DETECTION & REMOVAL
   - Calculate IQR for each numeric column
   - Remove rows outside 1.5×IQR bounds
   - Report: Z outliers removed
    ↓
5. RANGE VALIDATION
   - Years: 1900-2030
   - Percentages/Rates: 0-1
   - Counts: ≥ 0
   - Dates: logically consistent
   - Report: W issues found and fixed
    ↓
6. NORMALIZATION (Optional)
   - Min-Max scaling to 0-1 for numeric columns
   - Create *_normalized versions
   - Keep original for reference
   - Report: V columns normalized
    ↓
[Cleaned Data]
```

### Example: Cleaning dataset_1 (legal_cases)

```
Original:     75,000 rows × 18 columns
↓ Remove 125 duplicates
              74,875 rows
↓ Fill 342 null filing_dates with median
              74,875 rows (72 cols updated)
↓ Type conversions (12 columns)
              74,875 rows
↓ Remove 1,203 outlier case_values
              73,672 rows
↓ Fix 89 invalid/future dates
              73,672 rows (89 corrections)
↓ Normalize case_value, damage_amount (2 cols)
              73,672 rows × 20 columns (2 new normalized cols)

Cleaned:      73,672 rows × 20 columns ✓
```

---

## Data Validation Rules (Step 3)

### Automatic Validations Applied:

```python
# Legal Cases
- case_id: REQUIRED, UNIQUE, NUMERIC
- case_name: REQUIRED, STRING, LENGTH < 500
- filing_date: REQUIRED, DATE, >= 1900, <= today
- case_status: ENUM [Open, Closed, Pending]
- case_type: ENUM [Criminal, Civil]
- case_value: OPTIONAL, NUMERIC, >= 0

# Sentencing
- sentencing_id: REQUIRED, UNIQUE, NUMERIC
- case_id: REQUIRED, NUMERIC, FK to legal_cases
- sentence_length: NUMERIC, >= 0
- If sentence_type = Prison: sentence_length > 0
- defendant_age: NUMERIC, 18-100 range
- prior_convictions: NUMERIC, >= 0
- recidivism_flag: OPTIONAL, BOOLEAN

# Judge Decisions
- decision_id: REQUIRED, UNIQUE, NUMERIC
- decision_confidence: NUMERIC, 0-1 range
- decision_type: ENUM [Guilty, Not Guilty, Acquittal, Mistrial]
- case_complexity: NUMERIC, 1-10 range
- If appeal_filed = False: appeal_successful = NULL

# Crime Statistics
- year: NUMERIC, 1990-2030
- offense_count: NUMERIC, >= 0
- arrest_count: NUMERIC, 0 <= arrest_count <= offense_count
- conviction_count: NUMERIC, 0 <= conviction_count <= arrest_count
- crime_rate: NUMERIC, 0-1 range
- solved_rate: NUMERIC, 0-1 range
- victim_count: NUMERIC, victim_count <= offense_count

# Court Proceedings
- proceeding_id: REQUIRED, UNIQUE, NUMERIC
- duration_minutes: NUMERIC, > 0, < 480
- attendees_count: NUMERIC, > 0
- proceeding_date: >= associated case filing_date
```

---

## Data Quality Metrics (Step 3)

For each dataset, calculate:

```
Completeness = (Total Cells - Null Cells) / Total Cells × 100
  Example: If 10,000 rows × 20 cols = 200,000 cells
           1,500 nulls = 99.25% complete

Uniqueness = Total Rows / Unique Rows (after dedup)
  Example: 73,672 cleaned rows (no duplicates) = 100% unique

Consistency = Logical consistency checks
  Example: 98.5% (only logical issues fixed)

Column-Level Quality:
  - Non-null counts
  - Unique value counts
  - Data type validation %
  - Range validation %
```

---

## Data Export Format (Step 4)

### Output Structure:

```
data/
└── hdfs/
    └── processed/
        ├── dataset_1_cleaned.parquet    ← For Spark processing
        ├── dataset_1_cleaned.csv        ← For Excel/inspection
        ├── dataset_1_cleaned.json       ← For schema preservation
        ├── dataset_2_cleaned.parquet
        ├── dataset_2_cleaned.csv
        ├── dataset_2_cleaned.json
        ... (3 formats × 5 datasets = 15 files)
```

### Why Multiple Formats?

- **Parquet**: Efficient columnar format, best for Spark/Big Data processing
- **CSV**: Human-readable, importable to Excel, spreadsheet tools
- **JSON**: Schema-preserving, importable to NoSQL, REST APIs

---

## Complete Pipeline Execution

```python
results = run_complete_pipeline()

# Returns:
{
    "imported_datasets": {
        "dataset_1": <DataFrame 75000×18>,
        "dataset_2": <DataFrame 45000×15>,
        ...
    },
    "cleaned_datasets": {
        "dataset_1": <DataFrame 73672×20>,
        "dataset_2": <DataFrame 44650×16>,
        ...
    },
    "import_summary": {
        "total_datasets": 5,
        "total_rows": 450500,
        "total_columns": 87,
        "datasets": {...}
    },
    "cleaning_report": {
        "total_datasets_cleaned": 5,
        "total_rows_removed": 1850,
        "total_duplicates_removed": 450,
        "total_outliers_removed": 1200,
        "datasets": {...}
    },
    "quality_metrics": {
        "dataset_1": {
            "completeness": 99.12,
            "uniqueness": 1.0,
            "consistency": 98.5,
            "columns": {...}
        },
        ...
    },
    "export_paths": {
        "dataset_1": {
            "parquet": "data/hdfs/processed/dataset_1_cleaned.parquet",
            "csv": "data/hdfs/processed/dataset_1_cleaned.csv",
            "json": "data/hdfs/processed/dataset_1_cleaned.json"
        },
        ...
    }
}
```

---

## Usage Example

```python
from data_import_preprocessing import (
    DataImporter, 
    DataCleaner, 
    DataQualityAnalyzer,
    DataExporter,
    run_complete_pipeline
)

# Run complete pipeline
results = run_complete_pipeline()

# Or use individual components:
importer = DataImporter()
datasets = importer.import_all_datasets()

cleaner = DataCleaner()
cleaned = cleaner.clean_all_datasets(datasets)
report = cleaner.get_cleaning_report()

analyzer = DataQualityAnalyzer()
metrics = analyzer.analyze_quality(cleaned)

exporter = DataExporter()
paths = exporter.export_datasets(cleaned)
```

---

## Summary

| Step | Input | Process | Output | Size |
|------|-------|---------|--------|------|
| 1. Import | HDFS Parquet | Read 5 files | 450K rows | ~700 KB |
| 2. Clean | Raw data | Dedup, validate, fix | 448K rows | ~650 KB |
| 3. Analyze | Cleaned data | Quality metrics | Metrics JSON | ~50 KB |
| 4. Export | Cleaned data | Parquet/CSV/JSON | 15 files | ~2 MB total |

**Total Time:** ~2-5 minutes for 500K rows on standard hardware
**Data Quality Improvement:** 99%+ complete, valid, consistent data
**Ready for:** ML pipeline, analytics, reporting, knowledge graphs
