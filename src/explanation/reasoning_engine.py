"""
Reasoning Engine Module
Generates explainable reasoning for predictions and decisions
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """Generate explainable reasoning for AI predictions."""
    
    def __init__(self):
        """Initialize reasoning engine."""
        self.explanation_templates = {
            'prediction': "Based on similar cases {cases}, we predict {outcome}",
            'similarity': "This case is {similarity_pct}% similar to case {case_id}",
            'bias': "Potential bias detected in {category}: {details}"
        }
        logger.info("ReasoningEngine initialized")
    
    def explain_prediction(self, prediction: Dict, similar_cases: List[str]) -> str:
        """
        Generate explanation for case outcome prediction.
        
        Args:
            prediction: Prediction result
            similar_cases: List of similar case IDs
            
        Returns:
            Human-readable explanation
        """
        try:
            outcome = prediction.get('outcome', 'UNKNOWN')
            confidence = prediction.get('confidence', 0.0)
            
            explanation = f"""
            Case Outcome Prediction:
            Predicted Outcome: {outcome}
            Confidence: {confidence:.2%}
            Similar Cases: {', '.join(similar_cases)}
            """
            
            return explanation.strip()
        
        except Exception as e:
            logger.error(f"Error generating prediction explanation: {str(e)}")
            return ""
    
    def explain_similarity(self, query_case: str, similar_cases: List[Dict]) -> str:
        """
        Generate explanation for case similarity.
        
        Args:
            query_case: Query case ID
            similar_cases: List of similar cases with scores
            
        Returns:
            Human-readable explanation
        """
        try:
            explanation = f"Cases similar to {query_case}:\n"
            
            for i, case in enumerate(similar_cases, 1):
                similarity = case.get('similarity_score', 0.0)
                explanation += f"{i}. Case ID: {case.get('case_id', 'N/A')} "
                explanation += f"(Similarity: {similarity:.2%})\n"
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error generating similarity explanation: {str(e)}")
            return ""
    
    def explain_bias(self, bias_detection: Dict) -> str:
        """
        Generate explanation for detected biases.
        
        Args:
            bias_detection: Bias detection results
            
        Returns:
            Human-readable explanation
        """
        try:
            explanation = "Bias Analysis Report:\n"
            
            if bias_detection.get('demographic_analysis'):
                explanation += f"Demographic Bias Score: {bias_detection['demographic_analysis'].get('bias_score', 0.0)}\n"
            
            if bias_detection.get('temporal_analysis'):
                explanation += f"Temporal Bias Detected: {bias_detection['temporal_analysis'].get('temporal_bias_score', 0.0)}\n"
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error generating bias explanation: {str(e)}")
            return ""


if __name__ == "__main__":

    print("Testing Reasoning Engine...\n")

    engine = ReasoningEngine()

    prediction_result = {
        "outcome": "Conviction",
        "confidence": 0.81
    }

    similar_cases = ["CASE_5", "CASE_7", "CASE_10"]

    bias_result = {
        "demographic_analysis": {"bias_score": 0.12},
        "temporal_analysis": {"temporal_bias_score": 0.05}
    }

    print("----- Prediction Explanation -----")
    print(engine.explain_prediction(prediction_result, similar_cases))

    print("\n----- Similarity Explanation -----")
    similar_case_details = [
        {"case_id": "CASE_5", "similarity_score": 0.92},
        {"case_id": "CASE_7", "similarity_score": 0.88},
        {"case_id": "CASE_10", "similarity_score": 0.85},
    ]

    print(engine.explain_similarity("CASE_2", similar_case_details))

    print("\n----- Bias Explanation -----")
    print(engine.explain_bias(bias_result))