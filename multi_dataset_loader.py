"""
Multi-Dataset Loader: Kaggle + HDFS Integration
Downloads 4-5 datasets from Kaggle and stores them in HDFS
"""

import os
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiDatasetLoader:
    """Download and manage multiple datasets from Kaggle"""
    
    def __init__(self, hdfs_path: str = "data/hdfs"):
        self.hdfs_path = hdfs_path
        self.datasets_config = {
            "dataset_1": {
                "name": "Legal Case Outcomes",
                "description": "US Legal Case outcomes and sentencing data",
                "kaggle_dataset": "usdoj/drugs-crime-arrests-by-state",
                "local_path": f"{hdfs_path}/legal_cases.csv",
                "type": "legal"
            },
            "dataset_2": {
                "name": "Criminal Sentencing Data",
                "description": "Federal sentencing statistics and demographics",
                "kaggle_dataset": "usdoj/federal-sentencing-data",
                "local_path": f"{hdfs_path}/sentencing.csv",
                "type": "sentencing"
            },
            "dataset_3": {
                "name": "Judge Decisions Dataset",
                "description": "Historical judge decisions and case outcomes",
                "kaggle_dataset": "jsaguiar/judicial-decision-prediction",
                "local_path": f"{hdfs_path}/judge_decisions.csv",
                "type": "judicial"
            },
            "dataset_4": {
                "name": "Crime Statistics",
                "description": "Crime statistics by geography and demographics",
                "kaggle_dataset": "cdc/crime-statistics",
                "local_path": f"{hdfs_path}/crime_stats.csv",
                "type": "statistics"
            },
            "dataset_5": {
                "name": "Court Proceedings",
                "description": "Court proceedings and legal document metadata",
                "kaggle_dataset": "usdoj/prosecutions-and-convictions",
                "local_path": f"{hdfs_path}/court_proceedings.csv",
                "type": "court"
            }
        }
        
        # Create HDFS structure
        os.makedirs(f"{hdfs_path}/input", exist_ok=True)
        os.makedirs(f"{hdfs_path}/output", exist_ok=True)
        os.makedirs(f"{hdfs_path}/processed", exist_ok=True)
        
    def download_datasets(self) -> Dict[str, str]:
        """
        Download datasets from Kaggle (or use synthetic if Kaggle unavailable)
        Returns: Dictionary of dataset names and local paths
        """
        print("\n[DATASETS] Loading from Kaggle or generating synthetic data...")
        downloaded = {}
        
        try:
            import kaggle
            print("  ✓ Kaggle API available - downloading real datasets")
            
            for dataset_id, config in self.datasets_config.items():
                try:
                    print(f"\n  → Downloading: {config['name']}")
                    # Download from Kaggle
                    kaggle.api.dataset_download_files(
                        config['kaggle_dataset'],
                        path=self.hdfs_path,
                        unzip=True
                    )
                    print(f"    ✓ Downloaded: {config['name']}")
                    downloaded[dataset_id] = config['local_path']
                except Exception as e:
                    print(f"    ⚠ Kaggle download failed: {e}, using synthetic instead")
                    downloaded[dataset_id] = self._generate_synthetic_dataset(
                        dataset_id, config
                    )
        except ImportError:
            print("  ⚠ Kaggle API not installed, generating synthetic datasets")
            print("  To download real datasets, install: pip install kaggle")
            for dataset_id, config in self.datasets_config.items():
                downloaded[dataset_id] = self._generate_synthetic_dataset(
                    dataset_id, config
                )
        
        return downloaded
    
    def _generate_synthetic_dataset(self, dataset_id: str, config: Dict) -> str:
        """Generate realistic synthetic dataset for testing"""
        print(f"  → Generating synthetic: {config['name']}")
        
        if dataset_id == "dataset_1":  # Legal Cases
            data = self._generate_legal_cases()
            filename = f"{self.hdfs_path}/input/legal_cases.csv"
            
        elif dataset_id == "dataset_2":  # Sentencing
            data = self._generate_sentencing_data()
            filename = f"{self.hdfs_path}/input/sentencing.csv"
            
        elif dataset_id == "dataset_3":  # Judge Decisions
            data = self._generate_judge_decisions()
            filename = f"{self.hdfs_path}/input/judge_decisions.csv"
            
        elif dataset_id == "dataset_4":  # Crime Stats
            data = self._generate_crime_stats()
            filename = f"{self.hdfs_path}/input/crime_stats.csv"
            
        elif dataset_id == "dataset_5":  # Court Proceedings
            data = self._generate_court_proceedings()
            filename = f"{self.hdfs_path}/input/court_proceedings.csv"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"    ✓ Generated: {len(df)} records")
        return filename
    
    def _generate_legal_cases(self) -> List[Dict]:
        """Generate synthetic legal case data"""
        import random
        crimes = ["Murder", "Theft", "Fraud", "Assault", "Drug Trafficking", "Cybercrime"]
        regions = ["North", "South", "East", "West", "Central"]
        
        data = []
        for i in range(250):
            data.append({
                "case_id": f"LEGAL_{i:04d}",
                "crime": random.choice(crimes),
                "year": random.randint(2015, 2024),
                "region": random.choice(regions),
                "verdict": random.choice(["Guilty", "Not Guilty", "Dismissed"]),
                "sentence_years": random.randint(0, 25),
                "evidence_count": random.randint(1, 20),
                "witness_count": random.randint(0, 15),
                "defendant_age": random.randint(18, 75),
                "prosecutor_win_rate": round(random.uniform(0.4, 0.95), 2)
            })
        return data
    
    def _generate_sentencing_data(self) -> List[Dict]:
        """Generate synthetic federal sentencing data"""
        import random
        offense_types = ["Drug", "Fraud", "Weapons", "White Collar", "Violent"]
        
        data = []
        for i in range(300):
            data.append({
                "offense_id": f"SENT_{i:04d}",
                "offense_type": random.choice(offense_types),
                "guideline_sentence": random.randint(6, 240),
                "actual_sentence": random.randint(0, 300),
                "defendant_gender": random.choice(["M", "F"]),
                "defendant_race": random.choice(["White", "Black", "Hispanic", "Asian"]),
                "defendant_education": random.choice(["High School", "College", "Graduate"]),
                "fine_amount": random.randint(1000, 500000),
                "prison_flag": random.choice([0, 1]),
                "year": random.randint(2015, 2024)
            })
        return data
    
    def _generate_judge_decisions(self) -> List[Dict]:
        """Generate synthetic judge decision data"""
        import random
        judges = [f"Judge_{i}" for i in range(1, 51)]
        
        data = []
        for i in range(280):
            data.append({
                "decision_id": f"JUDGE_{i:04d}",
                "judge_name": random.choice(judges),
                "case_type": random.choice(["Civil", "Criminal", "Family", "Corporate"]),
                "plaintiff_won": random.choice([0, 1]),
                "decision_time_days": random.randint(30, 730),
                "case_complexity": random.choice(["Low", "Medium", "High"]),
                "judge_experience_years": random.randint(5, 40),
                "appeal_filed": random.choice([0, 1]),
                "appeal_success": random.choice([0, 1, None]),
                "year": random.randint(2015, 2024)
            })
        return data
    
    def _generate_crime_stats(self) -> List[Dict]:
        """Generate synthetic crime statistics"""
        import random
        
        data = []
        regions = ["North", "South", "East", "West", "Central", "Northeast", "Southeast"]
        for i in range(200):
            data.append({
                "stat_id": f"CRIME_{i:04d}",
                "region": random.choice(regions),
                "crimes_reported": random.randint(100, 5000),
                "arrests_made": random.randint(50, 3000),
                "convictions": random.randint(30, 2000),
                "conviction_rate": round(random.uniform(0.3, 0.9), 2),
                "violent_crimes": random.randint(10, 500),
                "property_crimes": random.randint(50, 2000),
                "drug_crimes": random.randint(20, 800),
                "year": random.randint(2015, 2024),
                "population": random.randint(100000, 5000000)
            })
        return data
    
    def _generate_court_proceedings(self) -> List[Dict]:
        """Generate synthetic court proceedings data"""
        import random
        
        data = []
        for i in range(220):
            data.append({
                "proceeding_id": f"COURT_{i:04d}",
                "court_name": random.choice(["District", "Superior", "Supreme", "Federal"]),
                "case_number": f"CASE_{random.randint(10000, 99999)}",
                "filing_date": f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                "trial_date": f"2023-{random.randint(7,12):02d}-{random.randint(1,28):02d}",
                "hearing_count": random.randint(1, 20),
                "defendant_count": random.randint(1, 5),
                "attorney_count": random.randint(2, 10),
                "document_count": random.randint(5, 100),
                "year": random.randint(2015, 2024)
            })
        return data
    
    def prepare_datasets_for_spark(self, datasets: Dict[str, str]) -> Dict[str, str]:
        """Convert all datasets to Parquet format for Spark processing"""
        print("\n[SPARK PREP] Converting datasets to Parquet format...")
        
        parquet_files = {}
        for dataset_id, csv_path in datasets.items():
            try:
                print(f"  → Converting {dataset_id}...")
                df = pd.read_csv(csv_path)
                parquet_path = csv_path.replace('.csv', '.parquet')
                df.to_parquet(parquet_path)
                parquet_files[dataset_id] = parquet_path
                print(f"    ✓ {dataset_id}: {len(df)} rows → {parquet_path}")
            except Exception as e:
                print(f"    ⚠ Error converting {dataset_id}: {e}")
        
        return parquet_files
    
    def save_dataset_manifest(self, datasets: Dict[str, str]) -> str:
        """Save manifest of all datasets"""
        manifest = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "total_datasets": len(datasets),
            "datasets": {}
        }
        
        for dataset_id, path in datasets.items():
            if os.path.exists(path):
                df = pd.read_csv(path)
                manifest["datasets"][dataset_id] = {
                    "path": path,
                    "rows": len(df),
                    "columns": list(df.columns),
                    "size_mb": os.path.getsize(path) / (1024 * 1024)
                }
        
        manifest_path = f"{self.hdfs_path}/datasets_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n[MANIFEST] Dataset manifest saved: {manifest_path}")
        return manifest_path


def main():
    """Download and prepare datasets"""
    loader = MultiDatasetLoader()
    
    # Download all datasets
    datasets = loader.download_datasets()
    
    # Display summary
    print("\n" + "="*70)
    print("DATASETS LOADED")
    print("="*70)
    for dataset_id, path in datasets.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            print(f"{dataset_id:15} | {len(df):6d} rows | {path}")
    
    # Prepare for Spark
    parquet_files = loader.prepare_datasets_for_spark(datasets)
    
    # Save manifest
    loader.save_dataset_manifest(datasets)
    
    print("\n✓ All datasets ready for Spark processing!")
    return datasets, parquet_files


if __name__ == "__main__":
    main()
