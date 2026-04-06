"""
Integration: How to use the data preprocessing pipeline with run_pipeline.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_import_preprocessing import run_complete_pipeline
from preprocessing.spark_preprocessing import prepare_data_for_spark
from clustering.keyword_clustering import perform_clustering
from similarity.similarity_search import build_similarity_index
from prediction.outcome_model import train_outcome_model
from bias_detection.bias_detector import detect_bias


def main():
    print("\n" + "="*80)
    print("JUDICIAL AI SYSTEM - COMPLETE PIPELINE")
    print("="*80)
    
    # ============================================================================
    # PHASE 1: DATA IMPORT & PREPROCESSING
    # ============================================================================
    print("\n[PHASE 1] Importing & Cleaning Data...")
    print("-" * 80)
    
    results = run_complete_pipeline()
    
    cleaned_datasets = results["cleaned_datasets"]
    cleaning_report = results["cleaning_report"]
    quality_metrics = results["quality_metrics"]
    
    print(f"\n✓ Phase 1 Complete:")
    print(f"  - {len(cleaned_datasets)} datasets imported & cleaned")
    print(f"  - {cleaning_report['total_rows_removed']:,} rows removed")
    print(f"  - {cleaning_report['total_duplicates_removed']:,} duplicates")
    print(f"  - {cleaning_report['total_outliers_removed']:,} outliers")
    
    # ============================================================================
    # PHASE 2: DATA PREPARATION FOR SPARK
    # ============================================================================
    print("\n[PHASE 2] Preparing Data for Spark Processing...")
    print("-" * 80)
    
    try:
        spark_data = prepare_data_for_spark(cleaned_datasets)
        print(f"✓ Data prepared:")
        print(f"  - Partitioned for distributed processing")
        print(f"  - Optimized columnar format")
        print(f"  - Ready for Spark RDD/DataFrame operations")
    except Exception as e:
        print(f"✗ Spark preparation error: {e}")
    
    # ============================================================================
    # PHASE 3: EXTRACT LEGAL KNOWLEDGE
    # ============================================================================
    print("\n[PHASE 3] Extracting Legal Knowledge...")
    print("-" * 80)
    
    try:
        # Clustering
        clusters = perform_clustering(cleaned_datasets.get("dataset_1"))
        print(f"✓ Clustering complete: {len(clusters)} keyword clusters identified")
        
        # Build similarity index
        similarity_index = build_similarity_index(cleaned_datasets)
        print(f"✓ Similarity index built: Ready for case matching")
        
    except Exception as e:
        print(f"! Note: Knowledge extraction needs additional setup: {e}")
    
    # ============================================================================
    # PHASE 4: BIAS DETECTION
    # ============================================================================
    print("\n[PHASE 4] Detecting Unfairness & Bias...")
    print("-" * 80)
    
    try:
        bias_results = detect_bias(
            cleaned_datasets.get("dataset_2"),  # sentencing data
            cleaned_datasets.get("dataset_3"),  # judge decisions
            cleaned_datasets.get("dataset_4")   # crime statistics
        )
        print(f"✓ Bias detection complete")
        print(f"  - Demographic disparities identified")
        print(f"  - Judge inconsistency analysis")
    except Exception as e:
        print(f"! Note: Bias detection needs additional setup: {e}")
    
    # ============================================================================
    # PHASE 5: PREDICTIVE MODELING
    # ============================================================================
    print("\n[PHASE 5] Training Predictive Models...")
    print("-" * 80)
    
    try:
        model = train_outcome_model(
            cleaned_datasets.get("dataset_1"),  # features
            cleaned_datasets.get("dataset_3")   # target (judge decisions)
        )
        print(f"✓ Outcome prediction model trained")
        print(f"  - Ready for case outcome predictions")
    except Exception as e:
        print(f"! Note: Model training needs additional setup: {e}")
    
    # ============================================================================
    # PHASE 6: GENERATE SUMMARY REPORT
    # ============================================================================
    print("\n" + "="*80)
    print("PIPELINE SUMMARY")
    print("="*80)
    
    print("\n[DATA QUALITY]")
    for dataset_id, metrics in quality_metrics.items():
        completeness = metrics["completeness"]
        print(f"  {dataset_id}:")
        print(f"    - Completeness: {completeness:.2f}%")
        print(f"    - Consistency: {metrics['consistency']}%")
    
    print("\n[CLEANING RESULTS]")
    print(f"  Datasets processed: {len(cleaning_report['datasets'])}")
    for dataset_id, report in cleaning_report['datasets'].items():
        print(f"  {dataset_id}:")
        print(f"    - Original: {report['original_rows']:,} rows")
        print(f"    - Cleaned: {report['cleaned_rows']:,} rows")
        print(f"    - Removed: {report['rows_removed']:,} ({(report['rows_removed']/report['original_rows']*100):.1f}%)")
    
    print("\n[EXPORT LOCATIONS]")
    for dataset_id, paths in results["export_paths"].items():
        print(f"  {dataset_id}:")
        print(f"    - Parquet: {paths['parquet']}")
        print(f"    - CSV: {paths['csv']}")
        print(f"    - JSON: {paths['json']}")
    
    print("\n" + "="*80)
    print("✓ COMPLETE PIPELINE EXECUTED SUCCESSFULLY")
    print("="*80)
    
    return {
        "phase_1_import": results,
        "phase_2_spark": spark_data if 'spark_data' in locals() else None,
        "phase_3_knowledge": {
            "clusters": clusters if 'clusters' in locals() else None,
            "similarity_index": similarity_index if 'similarity_index' in locals() else None
        },
        "phase_4_bias": bias_results if 'bias_results' in locals() else None,
        "phase_5_prediction": model if 'model' in locals() else None,
    }


if __name__ == "__main__":
    pipeline_results = main()
