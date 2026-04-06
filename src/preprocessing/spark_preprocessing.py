"""
Apache Spark Preprocessing Module
Handles distributed text preprocessing using Spark
"""

import logging
from typing import Optional

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, lower, regexp_replace
except ImportError:
    logging.warning("PySpark not installed. Install with: pip install pyspark")

logger = logging.getLogger(__name__)


class SparkPreprocessor:
    """Distributed text preprocessing using Apache Spark."""
    
    def __init__(self, app_name: str = "Judicial-AI-Preprocessing"):
        """
        Initialize Spark preprocessor.
        
        Args:
            app_name: Spark application name
        """
        try:
            self.spark = SparkSession.builder.appName(app_name).getOrCreate()
            logger.info("Spark session initialized")
        except Exception as e:
            logger.error(f"Error initializing Spark: {str(e)}")
            self.spark = None
    
    def normalize_text(self, df, text_column: str):
        """
        Normalize text: lowercase, remove special characters.
        
        Args:
            df: Spark DataFrame
            text_column: Name of text column
            
        Returns:
            DataFrame with normalized text
        """
        if self.spark is None:
            logger.error("Spark session not initialized")
            return None
        
        df = df.withColumn(
            text_column,
            lower(col(text_column))
        )
        return df
    
    def remove_special_chars(self, df, text_column: str):
        """
        Remove special characters from text.
        
        Args:
            df: Spark DataFrame
            text_column: Name of text column
            
        Returns:
            DataFrame with cleaned text
        """
        df = df.withColumn(
            text_column,
            regexp_replace(col(text_column), "[^a-zA-Z0-9\\s]", "")
        )
        return df
    
    def stop(self):
        """Stop Spark session."""
        if self.spark:
            self.spark.stop()
            logger.info("Spark session stopped")


if __name__ == "__main__":
    preprocessor = SparkPreprocessor()
