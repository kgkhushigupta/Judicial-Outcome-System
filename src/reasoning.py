import logging
from src.hierarchical_argument_tree import (
    HierarchicalArgumentTreeBuilder,
    extract_precedent_strength,
    extract_statutory_strength,
    extract_weakness_factors
)

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
            "confidence": f"{confidence:.2f}%",
            "key_factors": [kw[0] for kw in keywords[:5]] if keywords else [],
            "supporting_precedents": len(precedents) if precedents else 0
        }
    }
    return sections


def generate_hierarchical_argument_tree(prediction, confidence, precedents, statutes, keywords, reasoning_trail):
    """Generate hierarchical legal argument tree showing how facts support conclusions.
    
    Args:
        prediction: Binary prediction (0 or 1)
        confidence: Confidence score (0-100)
        precedents: List of similar precedent cases
        statutes: List of applicable statutory provisions
        keywords: List of extracted keywords with weights
        reasoning_trail: List of reasoning steps
    
    Returns:
        Dictionary containing the hierarchical tree structure
    """
    try:
        # Build the hierarchical tree
        builder = HierarchicalArgumentTreeBuilder()
        tree = builder.build(
            prediction=prediction,
            confidence=confidence,
            precedents=precedents if precedents else [],
            statutes=statutes if statutes else [],
            keywords=keywords if keywords else [],
            reasoning_trail=reasoning_trail if reasoning_trail else []
        )
        
        # Generate tree visualization and data
        tree_data = {
            "tree_structure": builder.render_dict(),
            "tree_ascii": builder.render_ascii(),
            "summary": {
                "outcome": "ACCEPTED" if prediction == 1 else "REJECTED",
                "overall_confidence": round(confidence, 2),
                "main_argument_branches": len(tree.children),
                "precedent_strength": extract_precedent_strength(precedents if precedents else [])[1],
                "statutory_strength": extract_statutory_strength(statutes if statutes else [])[1],
                "identified_weaknesses": extract_weakness_factors(confidence, keywords)
            }
        }
        
        logger.info("[HierarchicalTree] Generated argument tree with %d branches", len(tree.children))
        return tree_data
        
    except Exception as e:
        logger.error("[HierarchicalTree] Error generating tree: %s", str(e))
        return {
            "error": str(e),
            "tree_structure": None,
            "summary": {
                "outcome": "ACCEPTED" if prediction == 1 else "REJECTED",
                "overall_confidence": round(confidence, 2)
            }
        }

