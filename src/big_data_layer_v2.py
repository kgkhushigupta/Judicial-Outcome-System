"""
Big Data Layer - Distributed Processing Demo
Implements Big Data patterns using Pandas + Spark (when available)
"""

import os
import logging
from typing import Optional, Tuple, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Suppress Spark warnings
os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
os.environ['TZ'] = 'UTC'


class DistributedDataProcessor:
    """
    Distributed data processing using available tools.
    Attempts Spark, gracefully falls back to pandas with partitioning simulation.
    """
    
    def __init__(self, num_partitions: int = 8):
        """
        Initialize processor.
        
        Args:
            num_partitions: Number of partitions for simulating distributed processing
        """
        self.num_partitions = num_partitions
        self.spark = None
        self.use_spark = False
        self._init_spark()
        
        if not self.use_spark:
            logger.info(f"✓ Using pandas with partition simulation ({num_partitions} partitions)")
    
    def _init_spark(self):
        """Try to initialize Spark"""
        try:
            from pyspark.sql import SparkSession
            import os
            
            # Suppress Spark logging
            os.environ['SPARK_LOG_DIR'] = '/tmp'
            
            self.spark = SparkSession.builder \
                .appName("judicial-big-data") \
                .master("local[*]") \
                .config("spark.driver.memory", "2g") \
                .config("spark.executor.memory", "1g") \
                .config("spark.sql.shuffle.partitions", str(self.num_partitions)) \
                .config("spark.driver.host", "127.0.0.1") \
                .config("spark.sql.warehouse.dir", "./spark_warehouse") \
                .config("spark.hadoop.hadoop.home.dir", "./") \
                .config("spark.hadoop.java.io.tmpdir", "./tmp") \
                .config("spark.network.timeout", "120") \
                .config("spark.executor.heartbeatInterval", "60") \
                .getOrCreate()
            
            # Suppress output
            self.spark.sparkContext.setLogLevel("ERROR")
            self.use_spark = True
            logger.info("✓ Apache Spark initialized (real distributed processing)")
            
        except Exception as e:
            logger.info("⚠ Spark not available, using pandas with partition simulation")
            self.use_spark = False
            self.spark = None
    
    def partitioned_processing(self, df: pd.DataFrame, 
                              processor_func) -> pd.DataFrame:
        """
        Process dataframe in partitions to simulate distributed computing.
        
        Args:
            df: Input dataframe
            processor_func: Function to apply to each partition
            
        Returns:
            Processed dataframe
        """
        # Split into partitions
        partitions = np.array_split(df, self.num_partitions)
        
        # Process each partition
        processed_parts = []
        for i, partition in enumerate(partitions):
            if len(partition) > 0:
                result = processor_func(partition)
                processed_parts.append(result)
        
        # Combine results
        result_df = pd.concat(processed_parts, ignore_index=True)
        logger.info(f"✓ Processed {len(df)} records across {len(processed_parts)} partitions")
        return result_df
    
    def distributed_clean_text(self, df: pd.DataFrame, text_col: str) -> pd.DataFrame:
        """
        Clean text in distributed manner (partitioned).
        """
        if self.use_spark:
            return self._spark_clean_text(df, text_col)
        else:
            return self._pandas_clean_text(df, text_col)
    
    def _spark_clean_text(self, df: pd.DataFrame, text_col: str) -> pd.DataFrame:
        """Clean text using Spark"""
        try:
            from pyspark.sql.functions import lower, regexp_replace, trim, col
            
            spark_df = self.spark.createDataFrame(df)
            
            # Clean using Spark SQL
            cleaned_df = spark_df \
                .withColumn(text_col, lower(col(text_col))) \
                .withColumn(text_col, regexp_replace(col(text_col), "[^a-zA-Z0-9\\s]", " ")) \
                .withColumn(text_col, trim(regexp_replace(col(text_col), "\\s+", " ")))
            
            result = cleaned_df.toPandas()
            logger.info(f"✓ Spark: Cleaned {len(result)} records (distributed)")
            return result
        except Exception as e:
            logger.error(f"Spark cleaning failed: {e}, falling back to pandas")
            return self._pandas_clean_text(df, text_col)
    
    def _pandas_clean_text(self, df: pd.DataFrame, text_col: str) -> pd.DataFrame:
        """Clean text using pandas (partitioned)"""
        import re
        
        def clean_partition(part):
            part = part.copy()
            part[text_col] = part[text_col].str.lower()
            part[text_col] = part[text_col].apply(
                lambda x: re.sub(r'[^a-zA-Z0-9\s]', ' ', str(x))
            )
            part[text_col] = part[text_col].apply(
                lambda x: re.sub(r'\s+', ' ', str(x)).strip()
            )
            return part
        
        result = self.partitioned_processing(df, clean_partition)
        logger.info(f"✓ Pandas+Partitions: Cleaned {len(result)} records")
        return result
    
    def get_stats(self, df: pd.DataFrame) -> dict:
        """Get statistics about dataset"""
        stats = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "partitions": self.num_partitions,
            "mode": "Spark" if self.use_spark else "Pandas+Partitions"
        }
        logger.info(f"✓ Dataset: {stats['row_count']} rows, "
                   f"{stats['partitions']} partitions ({stats['mode']})")
        return stats
    
    def close(self):
        """Close Spark session if active"""
        if self.spark:
            try:
                self.spark.stop()
                logger.info("✓ Spark session closed")
            except:
                pass


class HdfsSimulator:
    """
    Simulates HDFS for local development.
    In production, would connect to actual HDFS cluster.
    """
    
    def __init__(self, base_path: str = "data/hdfs"):
        """Initialize HDFS simulator"""
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        logger.info(f"✓ HDFS simulator initialized at {base_path}")
    
    def put(self, local_path: str, hdfs_path: str) -> bool:
        """Upload file to simulated HDFS"""
        try:
            import shutil
            full_path = os.path.join(self.base_path, hdfs_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            shutil.copy2(local_path, full_path)
            logger.info(f"✓ HDFS: Uploaded {hdfs_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Upload failed: {e}")
            return False
    
    def get(self, hdfs_path: str, local_path: str) -> bool:
        """Download file from simulated HDFS"""
        try:
            import shutil
            full_path = os.path.join(self.base_path, hdfs_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            shutil.copy2(full_path, local_path)
            logger.info(f"✓ HDFS: Downloaded {hdfs_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Download failed: {e}")
            return False
    
    def ls(self, hdfs_path: str) -> List[str]:
        """List files in HDFS directory"""
        try:
            full_path = os.path.join(self.base_path, hdfs_path)
            if os.path.exists(full_path):
                files = os.listdir(full_path)
                logger.info(f"✓ HDFS: Listed {len(files)} files in {hdfs_path}")
                return files
            return []
        except Exception as e:
            logger.error(f"✗ List failed: {e}")
            return []


if __name__ == "__main__":
    print("\n" + "="*70)
    print("BIG DATA LAYER - Distributed Processing Demo")
    print("="*70 + "\n")
    
    # Initialize processor
    processor = DistributedDataProcessor(num_partitions=8)
    
    # Create sample data
    sample_df = pd.DataFrame({
        'case_id': ['CASE_0001', 'CASE_0002', 'CASE_0003'],
        'text': [
            'The DEFENDANT was charged with FRAUD!!!',
            'Witness TESTIFIED about the INCIDENT',
            'Judge RULED guilty with EVIDENCE'
        ]
    })
    
    print("Input Data:")
    print(sample_df)
    
    # Process
    print("\nProcessing with distributed text cleaning...")
    cleaned_df = processor.distributed_clean_text(sample_df, 'text')
    
    print("\nCleaned Data:")
    print(cleaned_df)
    
    # Stats
    stats = processor.get_stats(cleaned_df)
    print(f"\nDataset Stats: {stats}")
    
    # HDFS demo
    print("\nHDFS Simulator Demo:")
    hdfs = HdfsSimulator()
    hdfs.put("requirements.txt", "input/requirements.txt")
    files = hdfs.ls("input")
    print(f"HDFS Files: {files}")
    
    processor.close()
    
    print("\n" + "="*70)
    print("✓ Big Data Layer Demo Complete!")
    print("="*70 + "\n")
