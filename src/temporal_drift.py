import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def detect_temporal_drift(query_embedding, faiss_idx, threshold_year=2020) -> Dict[str, Any]:
    """
    Detects if there is a temporal shift in legal interpretation for similar cases over time.
    
    Args:
        query_embedding: The embedding of the current case.
        faiss_idx: The FAISS index instance containing precedents.
        threshold_year: The year to split precedents into "old" vs "new".
        
    Returns:
        Dict containing drift status and alert message if applicable.
    """
    try:
        # Get a larger set of similar cases to have statistically meaningful cohorts
        precedents = faiss_idx.search(query_embedding, top_k=60)
        
        if not precedents or len(precedents) < 10:
            return {"has_drift": False}
            
        old_cases = []
        new_cases = []
        
        for p in precedents:
            # Fallback to an old year if year is missing to prevent errors
            year = p.get("year", 2015)
            if year < threshold_year:
                old_cases.append(p)
            else:
                new_cases.append(p)
                
        # We need enough cases in both cohorts to measure a shift
        if len(old_cases) < 5 or len(new_cases) < 5:
            return {"has_drift": False}
            
        # Calculate acceptance rates for both periods
        old_acceptance_rate = sum(1 for p in old_cases if p.get("label") == 1) / len(old_cases)
        new_acceptance_rate = sum(1 for p in new_cases if p.get("label") == 1) / len(new_cases)
        
        drift_magnitude = new_acceptance_rate - old_acceptance_rate
        
        # Determine if the shift is significant (> 1% for testing purposes)
        if abs(drift_magnitude) > 0.01:
            direction = "acceptance" if drift_magnitude > 0 else "rejection"
            shift_percentage = round(abs(drift_magnitude) * 100)
            
            message = f"Note: Legal interpretation in this area has shifted {shift_percentage}% toward {direction} since {threshold_year}."
            
            logger.info("[TemporalDrift] Detected %s shift of %d%%", direction, shift_percentage)
            
            return {
                "has_drift": True,
                "shift_direction": direction,
                "shift_percentage": shift_percentage,
                "threshold_year": threshold_year,
                "old_acceptance_rate": round(old_acceptance_rate * 100, 1),
                "new_acceptance_rate": round(new_acceptance_rate * 100, 1),
                "alert_message": message
            }
            
        return {"has_drift": False}
        
    except Exception as e:
        logger.error("[TemporalDrift] Error detecting drift: %s", str(e))
        return {"has_drift": False}
