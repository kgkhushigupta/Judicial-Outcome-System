import logging
logger = logging.getLogger(__name__)

def generate_explanation(reasoning_path, predicted_outcome):
    outcome_str = "Accepted/Allowed" if predicted_outcome == 1 else "Rejected/Dismissed"
    steps = reasoning_path if reasoning_path else []
    statute_refs = [s for s in steps if "Statute" in s or "Section" in s]
    statute_text = ""
    if statute_refs:
        statute_text = f" The applicable statutory provisions, namely {'; '.join(statute_refs[:2])}, have been duly considered."

    paragraph = (
        f"Upon meticulous examination of the factual matrix presented before this Court, "
        f"and having regard to the submissions advanced by the learned counsel for both parties, "
        f"the relevant statutory provisions and judicial precedents have been carefully analyzed.{statute_text} "
        f"The precedent analysis conducted through hierarchical semantic vector clustering reveals a pattern "
        f"consistent with established judicial reasoning in analogous matters. "
        f"Having considered the totality of circumstances, the weight of evidence, and the applicable legal principles, "
        f"this Court is of the considered opinion that the matter warrants a determination of: {outcome_str}. "
        f"This assessment is corroborated by the convergence of multiple analytical vectors including "
        f"statutory alignment, precedent similarity, and factual pattern recognition, "
        f"achieving a high degree of confidence in the predicted judicial outcome."
    )
    return paragraph

def generate_structured_reasoning(trail, prediction, confidence, keywords, precedents):
    sections = {
        "factual_analysis": trail[0] if len(trail) > 0 else "Case facts analyzed.",
        "statutory_framework": [s for s in trail if "Statute" in s or "Section" in s],
        "precedent_analysis": [s for s in trail if "precedent" in s.lower() or "FAISS" in s],
        "predictive_reasoning": [s for s in trail if "prediction" in s.lower() or "synthesized" in s.lower()],
        "conclusion": {
            "outcome": "ACCEPTED" if prediction == 1 else "REJECTED",
            "confidence": f"{confidence * 100:.2f}%",
            "key_factors": [kw[0] for kw in keywords[:5]] if keywords else [],
            "supporting_precedents": len(precedents) if precedents else 0
        }
    }
    return sections
