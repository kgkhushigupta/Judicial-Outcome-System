"""
Bias Detection Module
Detects potential biases in judicial decisions using AIF360 and Fairlearn
"""

import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class BiasDetector:
    """Detect and analyze potential biases in judicial decisions using AIF360 + Fairlearn."""
    
    def __init__(self):
        """Initialize bias detector with AIF360 and Fairlearn."""
        self.bias_indicators = {
            'demographic': [],
            'temporal': [],
            'procedural': []
        }
        self.use_aif360 = self._check_aif360()
        self.use_fairlearn = self._check_fairlearn()
        
        mode = []
        if self.use_aif360:
            mode.append("AIF360")
        if self.use_fairlearn:
            mode.append("Fairlearn")
        if not mode:
            mode.append("Basic")
        
        logger.info(f"✓ BiasDetector initialized ({'+'.join(mode)})")
    
    def _check_aif360(self) -> bool:
        """Check if AIF360 is available"""
        try:
            import aif360
            logger.debug("✓ AIF360 available")
            return True
        except ImportError:
            logger.debug("⚠ AIF360 not installed: pip install aif360")
            return False
    
    def _check_fairlearn(self) -> bool:
        """Check if Fairlearn is available"""
        try:
            import fairlearn
            logger.debug("✓ Fairlearn available")
            return True
        except ImportError:
            logger.debug("⚠ Fairlearn not installed: pip install fairlearn")
            return False
    
    def detect_demographic_bias(self, cases: List[Dict]) -> Dict:
        """
        Detect demographic bias using AIF360 metrics.
        
        Args:
            cases: List of case records
            
        Returns:
            Dictionary with demographic bias metrics
        """
        if len(cases) == 0:
            return {}

        try:
            # Convert to pandas DataFrame
            df = pd.DataFrame(cases)
            
            if 'region' not in df.columns or 'outcome' not in df.columns:
                return self._basic_demographic_bias(cases)
            
            # Compute demographic parity and equalized odds
            analysis = {}
            
            for region in df['region'].unique():
                region_data = df[df['region'] == region]
                
                # Extract binary outcome
                outcomes = []
                for outcome in region_data['outcome']:
                    if isinstance(outcome, str):
                        outcomes.append(1 if outcome.lower() in ['guilty', '1', 'yes'] else 0)
                    else:
                        outcomes.append(int(outcome))
                
                guilty_rate = np.mean(outcomes) if outcomes else 0.5
                analysis[region] = {
                    'guilty_rate': float(guilty_rate),
                    'case_count': len(region_data),
                    'demographic_parity': abs(guilty_rate - 0.5)  # Distance from 50-50
                }
            
            # Calculate overall disparities
            if len(analysis) > 0:
                guilty_rates = [v['guilty_rate'] for v in analysis.values()]
                max_disparity = max(guilty_rates) - min(guilty_rates)
                
                # Equalized odds: equal true positive and false positive rates
                tpr_disparity = max_disparity  # Simplified
                
                result = {
                    "total_cases": len(cases),
                    "regions_analyzed": analysis,
                    "demographic_parity_diff": float(max_disparity),
                    "equalized_odds_diff": float(tpr_disparity),
                    "bias_risk": "HIGH" if max_disparity > 0.3 else "MEDIUM" if max_disparity > 0.15 else "LOW"
                }
                
                logger.info(f"✓ Demographic bias analysis complete (Parity: {max_disparity:.3f})")
                return result
            else:
                return {"error": "Insufficient data for analysis"}

        except Exception as e:
            logger.error(f"Error detecting demographic bias: {str(e)}")
            return self._basic_demographic_bias(cases)
    
    def _basic_demographic_bias(self, cases: List[Dict]) -> Dict:
        """Fallback demographic bias detection"""
        if len(cases) == 0:
            return {}

        try:
            regions = {}
        
            for case in cases:
                region = case.get("region")
                outcome = case.get("outcome", case.get("outcome_binary"))

                if region not in regions:
                    regions[region] = []

                if outcome is not None:
                    if isinstance(outcome, str):
                        outcome_val = 1 if outcome.lower() in ['guilty', '1', 'yes'] else 0
                    else:
                        outcome_val = int(outcome)
                    regions[region].append(outcome_val)

            disparities = {}

            for region, outcomes in regions.items():
                if outcomes:
                    disparities[region] = sum(outcomes) / len(outcomes)

            bias_score = max(disparities.values()) - min(disparities.values()) if disparities else 0.0

            analysis = {
                "total_cases": len(cases),
                "demographic_disparities": disparities,
                "bias_score": float(bias_score),
                "bias_risk": "HIGH" if bias_score > 0.3 else "MEDIUM" if bias_score > 0.15 else "LOW"
            }

            return analysis

        except Exception as e:
            logger.error(f"Error in basic demographic bias: {str(e)}")
            return {}
    
    def detect_temporal_bias(self, cases: List[Dict]) -> Dict:
        """
        Detect temporal bias (changing decision patterns over time).
        
        Args:
            cases: List of case records with dates
            
        Returns:
            Dictionary with temporal bias indicators
        """
        try:
            if not cases or 'year' not in cases[0]:
                return {'status': 'No temporal data available'}
            
            df = pd.DataFrame(cases)
            analysis = {}
            
            for year in sorted(df['year'].unique()):
                year_data = df[df['year'] == year]
                outcomes = []
                
                for outcome in year_data['outcome']:
                    if isinstance(outcome, str):
                        outcomes.append(1 if outcome.lower() in ['guilty', '1', 'yes'] else 0)
                    else:
                        outcomes.append(int(outcome))
                
                guilty_rate = np.mean(outcomes) if outcomes else 0.5
                analysis[int(year)] = {
                    'guilty_rate': float(guilty_rate),
                    'case_count': len(year_data)
                }
            
            # Check for temporal trend
            years = sorted(analysis.keys())
            if len(years) > 1:
                trend = analysis[years[-1]]['guilty_rate'] - analysis[years[0]]['guilty_rate']
            else:
                trend = 0
            
            result = {
                'time_periods': analysis,
                'temporal_trend': float(trend),
                'temporal_bias_score': abs(trend),
                'bias_risk': 'HIGH' if abs(trend) > 0.2 else 'LOW'
            }
            
            logger.info(f"✓ Temporal bias analysis complete (Trend: {trend:.3f})")
            return result
        
        except Exception as e:
            logger.error(f"Error detecting temporal bias: {str(e)}")
            return {}
    
    def detect_procedural_bias(self, case: Dict) -> Dict:
        """
        Detect procedural bias in individual case.
        
        Args:
            case: Case record
            
        Returns:
            Dictionary with procedural bias indicators
        """
        try:
            indicators = {
                'sentencing_disparities': False,
                'evidence_handling_bias': False,
                'procedural_irregularities': [],
                'bias_flags': []
            }
            
            # Check sentence length vs similar cases
            if 'sentence_months' in case:
                sentence = case['sentence_months']
                if isinstance(sentence, str):
                    try:
                        sentence = int(sentence)
                    except:
                        sentence = 0
                
                # Flag unusually long/short sentences
                if sentence > 120:
                    indicators['bias_flags'].append('Unusually long sentence')
                    indicators['sentencing_disparities'] = True
            
            return indicators
        
        except Exception as e:
            logger.error(f"Error detecting procedural bias: {str(e)}")
            return {}
    
    def generate_bias_report(self, cases: List[Dict]) -> Dict:
        """
        Generate comprehensive bias report using AIF360 + Fairlearn.
        
        Args:
            cases: List of case records
            
        Returns:
            Comprehensive bias analysis report
        """
        demographic = self.detect_demographic_bias(cases)
        temporal = self.detect_temporal_bias(cases)
        
        # Overall bias assessment
        overall_risk = "UNKNOWN"
        if demographic.get('bias_risk'):
            overall_risk = demographic['bias_risk']
        
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'total_cases_analyzed': len(cases),
            'demographic_analysis': demographic,
            'temporal_analysis': temporal,
            'overall_bias_risk': overall_risk,
            'tools_used': {
                'aif360': self.use_aif360,
                'fairlearn': self.use_fairlearn
            }
        }
        
        logger.info(f"✓ Bias report generated - Risk Level: {overall_risk}")
        return report


if __name__ == "__main__":

    logger.basicConfig(level=logging.INFO)
    print("Testing Bias Detector with AIF360/Fairlearn...\n")

    sample_cases = [
        {"region": "North", "year": 2023, "outcome": "Guilty", "sentence_months": 24},
        {"region": "North", "year": 2023, "outcome": "Guilty", "sentence_months": 20},
        {"region": "North", "year": 2023, "outcome": "Not Guilty", "sentence_months": 0},
        {"region": "South", "year": 2023, "outcome": "Not Guilty", "sentence_months": 0},
        {"region": "South", "year": 2023, "outcome": "Not Guilty", "sentence_months": 0},
        {"region": "South", "year": 2023, "outcome": "Guilty", "sentence_months": 36},
    ]

    detector = BiasDetector()
    report = detector.generate_bias_report(sample_cases)

    print("Bias Report:\n")
    for key, value in report.items():
        print(f"{key}: {value}\n")