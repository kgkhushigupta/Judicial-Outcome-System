"""
Outcome Prediction Model
Predicts legal case outcomes using XGBoost machine learning
"""

import logging
import numpy as np
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class OutcomePredictor:
    """Predict case outcomes using XGBoost machine learning models."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize outcome predictor with XGBoost.
        
        Args:
            model_path: Path to trained model file
        """
        self.model = None
        self.model_path = model_path
        self.feature_names = []
        self.use_xgboost = self._check_xgboost()
        
        if model_path:
            self.load_model(model_path)
        
        logger.info(f"✓ OutcomePredictor initialized ({'XGBoost' if self.use_xgboost else 'Fallback'})")
    
    def _check_xgboost(self) -> bool:
        """Check if XGBoost is available"""
        try:
            import xgboost as xgb
            logger.debug("✓ XGBoost available")
            return True
        except ImportError:
            logger.warning("⚠ XGBoost not installed: pip install xgboost")
            return False
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray) -> bool:
        """
        Train outcome prediction model using XGBoost.
        
        Args:
            X_train: Training features (n_samples, n_features)
            y_train: Training labels (0=Not Guilty, 1=Guilty)
            
        Returns:
            True if training successful
        """
        try:
            # Use XGBoost if available, fallback to RandomForest
            if self.use_xgboost:
                return self._train_xgboost(X_train, y_train)
            else:
                return self._train_randomforest(X_train, y_train)
        
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return False
    
    def _train_xgboost(self, X_train: np.ndarray, y_train: np.ndarray) -> bool:
        """Train XGBoost classifier"""
        try:
            import xgboost as xgb
            
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric='logloss'
            )
            
            self.model.fit(
                X_train, y_train,
                verbose=False,
                eval_set=[(X_train, y_train)],
                early_stopping_rounds=None
            )
            
            logger.info(f"✓ XGBoost model trained on {len(X_train)} samples")
            return True
        
        except Exception as e:
            logger.error(f"XGBoost training failed: {e}, using RandomForest")
            return self._train_randomforest(X_train, y_train)
    
    def _train_randomforest(self, X_train: np.ndarray, y_train: np.ndarray) -> bool:
        """Fallback: Train RandomForest classifier"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            logger.info(f"✓ RandomForest model trained on {len(X_train)} samples (fallback)")
            return True
        
        except Exception as e:
            logger.error(f"RandomForest training also failed: {e}")
            return False
    
    def predict(self, features: np.ndarray) -> Dict:
        """
        Predict case outcome.
        
        Args:
            features: Case features (1D array)
            
        Returns:
            Prediction results with confidence and feature importance
        """
        if self.model is None:
            logger.error("Model not trained or loaded")
            return {"outcome": 0, "confidence": 0.5, "probabilities": [0.5, 0.5]}
        
        try:
            # Reshape for single prediction
            features_2d = features.reshape(1, -1) if features.ndim == 1 else features
            
            prediction = self.model.predict(features_2d)[0]
            probabilities = self.model.predict_proba(features_2d)[0]
            
            result = {
                'outcome': int(prediction),
                'outcome_label': 'Guilty' if prediction == 1 else 'Not Guilty',
                'probabilities': probabilities.tolist(),
                'confidence': float(np.max(probabilities))
            }
            
            # Add feature importance if available
            if hasattr(self.model, 'feature_importances_'):
                result['feature_importance'] = self.model.feature_importances_.tolist()
            
            return result
        
        except Exception as e:
            logger.error(f"Error predicting outcome: {str(e)}")
            return {"outcome": 0, "confidence": 0.5, "probabilities": [0.5, 0.5]}
    
    def batch_predict(self, features_list: List[np.ndarray]) -> List[Dict]:
        """
        Predict outcomes for multiple cases.
        
        Args:
            features_list: List of case features
            
        Returns:
            List of prediction results
        """
        predictions = [self.predict(features) for features in features_list]
        logger.info(f"✓ Made {len(predictions)} predictions")
        return predictions
    
    def get_feature_importance(self) -> Optional[np.ndarray]:
        """Get feature importance scores from the model"""
        if self.model is None or not hasattr(self.model, 'feature_importances_'):
            return None
        
        return self.model.feature_importances_
    
    def save_model(self, filepath: str) -> bool:
        """Save trained model to file."""
        try:
            import pickle
            with open(filepath, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"✓ Model saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Load trained model from file."""
        try:
            import pickle
            with open(filepath, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"✓ Model loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False


if __name__ == "__main__":
    # Test model
    import pandas as pd
    
    predictor = OutcomePredictor()
    
    # Create dummy training data
    X_train = np.random.randn(100, 10)
    y_train = np.random.randint(0, 2, 100)
    
    # Train
    if predictor.train_model(X_train, y_train):
        # Test prediction
        test_features = np.random.randn(10)
        result = predictor.predict(test_features)
        print(f"Prediction: {result}")


if __name__ == "__main__":

    print("Testing Outcome Prediction Model...\n")

    # Create sample training data
    X_train = np.random.rand(100, 10)   # 100 cases, 10 features
    y_train = np.random.randint(0, 2, 100)  # Binary outcomes

    # X_train = np.random.rand(100, 10)
    # # create a rule-based label
    # y_train = (X_train[:,0] + X_train[:,1] > 1).astype(int)

    predictor = OutcomePredictor()

    # Train model
    success = predictor.train_model(X_train, y_train)

    if success:
        print("Model trained successfully")

        # Test prediction
        test_case = np.random.rand(10)

        result = predictor.predict(test_case)

        print("\nPrediction Result:")
        print("Outcome:", result["outcome"])
        print("Confidence:", result["confidence"])
        print("Probabilities:", result["probabilities"])

    else:
        print("Model training failed")