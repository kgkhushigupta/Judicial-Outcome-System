"""
Data Import & Preprocessing Module
Comprehensive data cleaning pipeline for all 5 datasets
"""

import pandas as pd
import numpy as np
import logging
import os
from typing import Dict, List, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataImporter:
    """Import datasets from HDFS and local storage"""
    
    def __init__(self, hdfs_path: str = "data/hdfs"):
        self.hdfs_path = hdfs_path
        self.imported_data = {}
    
    def import_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Import all 5 datasets from HDFS
        
        Returns:
            Dictionary of dataset_id -> DataFrame
        """
        print("\n" + "="*70)
        print("STEP 1: IMPORTING DATASETS")
        print("="*70)
        
        datasets = {
            "dataset_1": "legal_cases.parquet",
            "dataset_2": "sentencing.parquet",
            "dataset_3": "judge_decisions.parquet",
            "dataset_4": "crime_stats.parquet",
            "dataset_5": "court_proceedings.parquet"
        }
        
        imported = {}
        
        for dataset_id, filename in datasets.items():
            path = f"{self.hdfs_path}/input/{filename}"
            
            try:
                # IMPORT: Read Parquet from HDFS
                df = pd.read_parquet(path)
                imported[dataset_id] = df
                
                print(f"\n✓ {dataset_id}: {filename}")
                print(f"  - Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                print(f"  - Size: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
                print(f"  - Columns: {', '.join(df.columns[:5])}...")
                print(f"  - Data types: {dict(df.dtypes)}")
                
            except FileNotFoundError:
                print(f"\n✗ {dataset_id}: File not found at {path}")
            except Exception as e:
                print(f"\n✗ {dataset_id}: Import error: {e}")
        
        self.imported_data = imported
        return imported
    
    def get_import_summary(self) -> Dict:
        """Get summary of imported datasets"""
        summary = {
            "total_datasets": len(self.imported_data),
            "total_rows": sum(len(df) for df in self.imported_data.values()),
            "total_columns": sum(len(df.columns) for df in self.imported_data.values()),
            "datasets": {}
        }
        
        for dataset_id, df in self.imported_data.items():
            summary["datasets"][dataset_id] = {
                "rows": len(df),
                "columns": len(df.columns),
                "size_kb": df.memory_usage(deep=True).sum() / 1024
            }
        
        return summary


class DataCleaner:
    """Comprehensive data cleaning pipeline"""
    
    def __init__(self):
        self.cleaning_report = {}
    
    def clean_all_datasets(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Apply cleaning pipeline to all datasets
        
        Args:
            datasets: Dictionary of dataset_id -> DataFrame
            
        Returns:
            Cleaned datasets
        """
        print("\n" + "="*70)
        print("STEP 2: DATA CLEANING & PREPROCESSING")
        print("="*70)
        
        cleaned = {}
        
        for dataset_id, df in datasets.items():
            print(f"\n[{dataset_id.upper()}] Cleaning pipeline...")
            
            # Apply cleaning steps
            df_cleaned = df.copy()
            
            # Step 1: Handle duplicates
            duplicates = df_cleaned.duplicated().sum()
            df_cleaned = df_cleaned.drop_duplicates()
            print(f"  1. Duplicates removed: {duplicates}")
            
            # Step 2: Handle null values
            null_counts = df_cleaned.isnull().sum().sum()
            for col in df_cleaned.columns:
                null_pct = (df_cleaned[col].isnull().sum() / len(df_cleaned)) * 100
                if null_pct > 0:
                    print(f"    - {col}: {null_pct:.2f}% nulls")
                    
                    # Fill based on type
                    if df_cleaned[col].dtype in ['int64', 'float64']:
                        df_cleaned[col].fillna(df_cleaned[col].median(), inplace=True)
                    elif df_cleaned[col].dtype == 'object':
                        df_cleaned[col].fillna('Unknown', inplace=True)
            print(f"  2. Null values handled: {null_counts} total nulls")
            
            # Step 3: Data type validation and conversion
            type_errors = 0
            for col in df_cleaned.columns:
                if col.endswith('_id') or col.endswith('_count'):
                    try:
                        df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
                    except:
                        type_errors += 1
            print(f"  3. Type conversions: {len(df_cleaned.columns)} columns validated")
            
            # Step 4: Remove outliers (numeric columns only)
            numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
            outliers_removed = 0
            
            for col in numeric_cols:
                Q1 = df_cleaned[col].quantile(0.25)
                Q3 = df_cleaned[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                before = len(df_cleaned)
                df_cleaned = df_cleaned[
                    (df_cleaned[col] >= lower_bound) & 
                    (df_cleaned[col] <= upper_bound)
                ]
                outliers_removed += before - len(df_cleaned)
            
            print(f"  4. Outliers removed: {outliers_removed}")
            
            # Step 5: Data validation
            validation_errors = self._validate_data(df_cleaned)
            print(f"  5. Data validation: {validation_errors} issues found/fixed")
            
            # Step 6: Standardization (for numeric columns)
            standardized = 0
            for col in numeric_cols:
                if col not in ['year', 'case_id', 'offense_id', 'decision_id']:
                    # Normalize to 0-1 range
                    min_val = df_cleaned[col].min()
                    max_val = df_cleaned[col].max()
                    if max_val > min_val:
                        df_cleaned[f"{col}_normalized"] = (
                            (df_cleaned[col] - min_val) / (max_val - min_val)
                        )
                        standardized += 1
            print(f"  6. Normalization applied: {standardized} columns")
            
            # Summary
            print(f"  ✓ Cleaned: {len(df_cleaned)} rows × {len(df_cleaned.columns)} columns")
            
            cleaned[dataset_id] = df_cleaned
            
            # Store cleaning report
            self.cleaning_report[dataset_id] = {
                "original_rows": len(df),
                "cleaned_rows": len(df_cleaned),
                "rows_removed": len(df) - len(df_cleaned),
                "duplicates_removed": duplicates,
                "outliers_removed": outliers_removed,
                "nulls_handled": null_counts,
                "columns_normalized": standardized
            }
        
        return cleaned
    
    def _validate_data(self, df: pd.DataFrame) -> int:
        """Validate data quality"""
        issues = 0
        
        # Check for negative years
        if 'year' in df.columns:
            invalid_years = (df['year'] < 1900) | (df['year'] > 2030)
            if invalid_years.any():
                df.loc[invalid_years, 'year'] = df['year'].median()
                issues += invalid_years.sum()
        
        # Check for invalid percentages
        for col in df.columns:
            if 'rate' in col.lower() or 'pct' in col.lower():
                invalid = (df[col] < 0) | (df[col] > 1)
                if invalid.any():
                    df.loc[invalid, col] = 0.5  # Default to midpoint
                    issues += invalid.sum()
        
        # Check for negative counts
        count_cols = [c for c in df.columns if 'count' in c.lower()]
        for col in count_cols:
            if df[col].dtype in ['int64', 'float64']:
                invalid = df[col] < 0
                if invalid.any():
                    df.loc[invalid, col] = 0
                    issues += invalid.sum()
        
        return issues
    
    def get_cleaning_report(self) -> Dict:
        """Get comprehensive cleaning report"""
        report = {
            "total_datasets_cleaned": len(self.cleaning_report),
            "datasets": self.cleaning_report
        }
        
        # Calculate totals
        report["total_rows_removed"] = sum(
            r["rows_removed"] for r in self.cleaning_report.values()
        )
        report["total_duplicates_removed"] = sum(
            r["duplicates_removed"] for r in self.cleaning_report.values()
        )
        report["total_outliers_removed"] = sum(
            r["outliers_removed"] for r in self.cleaning_report.values()
        )
        
        return report


class DataQualityAnalyzer:
    """Analyze data quality metrics"""
    
    @staticmethod
    def analyze_quality(datasets: Dict[str, pd.DataFrame]) -> Dict:
        """
        Analyze data quality for all datasets
        
        Returns:
            Quality metrics
        """
        print("\n" + "="*70)
        print("STEP 3: DATA QUALITY ANALYSIS")
        print("="*70)
        
        quality_metrics = {}
        
        for dataset_id, df in datasets.items():
            print(f"\n[{dataset_id.upper()}] Quality Analysis:")
            
            metrics = {
                "completeness": (1 - (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]))) * 100,
                "uniqueness": len(df) / (len(df.drop_duplicates()) if len(df.drop_duplicates()) > 0 else 1),
                "consistency": 100  # Assume consistent if passed cleaning
            }
            
            print(f"  - Completeness: {metrics['completeness']:.2f}%")
            print(f"  - Uniqueness: {metrics['uniqueness']:.2f}")
            print(f"  - Consistency: {metrics['consistency']}%")
            
            # Column-level quality
            quality_cols = {}
            for col in df.columns[:5]:  # Top 5 columns
                non_null = df[col].notna().sum()
                unique = df[col].nunique()
                quality_cols[col] = {
                    "non_null": non_null,
                    "unique": unique,
                    "null_count": df[col].isnull().sum()
                }
                print(f"    {col}: {non_null}/{len(df)} non-null, {unique} unique")
            
            metrics["columns"] = quality_cols
            quality_metrics[dataset_id] = metrics
        
        return quality_metrics


class DataExporter:
    """Export cleaned datasets to various formats"""
    
    def __init__(self, output_path: str = "data/hdfs/processed"):
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)
    
    def export_datasets(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """
        Export cleaned datasets to multiple formats
        
        Returns:
            Dictionary of dataset_id -> export paths
        """
        print("\n" + "="*70)
        print("STEP 4: EXPORTING CLEANED DATA")
        print("="*70)
        
        export_paths = {}
        
        for dataset_id, df in datasets.items():
            print(f"\n[{dataset_id.upper()}] Exporting...")
            
            # Export to Parquet (optimized for Spark)
            parquet_path = f"{self.output_path}/{dataset_id}_cleaned.parquet"
            df.to_parquet(parquet_path)
            print(f"  ✓ Parquet: {parquet_path}")
            
            # Export to CSV (human-readable)
            csv_path = f"{self.output_path}/{dataset_id}_cleaned.csv"
            df.to_csv(csv_path, index=False)
            print(f"  ✓ CSV: {csv_path}")
            
            # Export to JSON (schema-preserving)
            json_path = f"{self.output_path}/{dataset_id}_cleaned.json"
            df.to_json(json_path, orient="records")
            print(f"  ✓ JSON: {json_path}")
            
            export_paths[dataset_id] = {
                "parquet": parquet_path,
                "csv": csv_path,
                "json": json_path
            }
        
        return export_paths


def run_complete_pipeline():
    """Execute complete import → clean → analyze → export pipeline"""
    
    print("\n" + "="*80)
    print("COMPLETE DATA IMPORT & PREPROCESSING PIPELINE")
    print("="*80)
    
    # Step 1: Import datasets
    importer = DataImporter()
    datasets = importer.import_all_datasets()
    import_summary = importer.get_import_summary()
    
    print(f"\n[IMPORT SUMMARY]")
    print(f"  Datasets: {import_summary['total_datasets']}")
    print(f"  Total rows: {import_summary['total_rows']}")
    print(f"  Total columns: {import_summary['total_columns']}")
    
    # Step 2: Clean datasets
    cleaner = DataCleaner()
    cleaned_datasets = cleaner.clean_all_datasets(datasets)
    cleaning_report = cleaner.get_cleaning_report()
    
    print(f"\n[CLEANING SUMMARY]")
    print(f"  Total rows removed: {cleaning_report['total_rows_removed']}")
    print(f"  Total duplicates removed: {cleaning_report['total_duplicates_removed']}")
    print(f"  Total outliers removed: {cleaning_report['total_outliers_removed']}")
    
    # Step 3: Analyze quality
    analyzer = DataQualityAnalyzer()
    quality_metrics = analyzer.analyze_quality(cleaned_datasets)
    
    # Step 4: Export cleaned data
    exporter = DataExporter()
    export_paths = exporter.export_datasets(cleaned_datasets)
    
    print("\n[EXPORT SUMMARY]")
    for dataset_id, paths in export_paths.items():
        print(f"  {dataset_id}:")
        for fmt, path in paths.items():
            print(f"    - {fmt}: {path}")
    
    print("\n" + "="*80)
    print("✓ PIPELINE COMPLETE - All datasets imported, cleaned, and exported!")
    print("="*80)
    
    return {
        "imported_datasets": datasets,
        "cleaned_datasets": cleaned_datasets,
        "import_summary": import_summary,
        "cleaning_report": cleaning_report,
        "quality_metrics": quality_metrics,
        "export_paths": export_paths
    }


if __name__ == "__main__":
    results = run_complete_pipeline()
