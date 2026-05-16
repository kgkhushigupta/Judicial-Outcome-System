import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class TreeNode:
    """Represents a node in the hierarchical argument tree."""
    name: str
    confidence: float  # 0.0 to 1.0
    description: str = ""
    children: List['TreeNode'] = None
    evidence: List[str] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.evidence is None:
            self.evidence = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "confidence": round(self.confidence, 4),
            "description": self.description,
            "evidence": self.evidence,
            "children": [child.to_dict() for child in self.children]
        }
    
    def to_ascii_tree(self, prefix="", is_last=True) -> str:
        """Convert node to ASCII tree representation."""
        connector = "└── " if is_last else "├── "
        confidence_str = f" ({self.confidence:.2f})" if self.confidence > 0 else ""
        result = f"{prefix}{connector}{self.name}{confidence_str}\n"
        
        if self.evidence:
            for i, evidence in enumerate(self.evidence):
                is_last_evidence = (i == len(self.evidence) - 1) and len(self.children) == 0
                evidence_connector = "└── " if is_last_evidence else "├── "
                result += f"{prefix}    {evidence_connector}{evidence}\n"
        
        for i, child in enumerate(self.children):
            is_last_child = (i == len(self.children) - 1)
            extension = "    " if is_last else "│   "
            result += child.to_ascii_tree(prefix + extension, is_last_child)
        
        return result


class HierarchicalArgumentTreeBuilder:
    """Builds hierarchical argument trees for legal case predictions."""
    
    def __init__(self):
        self.root = None
        self.outcome = None
        self.overall_confidence = 0.0
    
    def build(self, 
              prediction: int, 
              confidence: float,
              precedents: List[Dict[str, Any]],
              statutes: List[Dict[str, str]],
              keywords: List[Tuple[str, float]],
              reasoning_trail: List[str]) -> TreeNode:
        """Build hierarchical tree from prediction components."""
        
        outcome_str = "ACCEPTED" if prediction == 1 else "REJECTED"
        self.outcome = outcome_str
        # Confidence comes as 0-100 from predictor. Convert to 0-1 for tree nodes
        self.overall_confidence = confidence / 100.0
        
        # Create root node
        self.root = TreeNode(
            name=f"Prediction: {outcome_str}",
            confidence=self.overall_confidence,
            description=f"Overall case outcome with {confidence:.1f}% confidence"
        )
        
        # Build branch 1: Precedent Alignment
        precedent_branch = self._build_precedent_branch(precedents, keywords)
        if precedent_branch:
            self.root.children.append(precedent_branch)
        
        # Build branch 2: Statutory Support
        statutory_branch = self._build_statutory_branch(statutes, reasoning_trail)
        if statutory_branch:
            self.root.children.append(statutory_branch)
        
        # Build branch 3: Weakness Analysis
        weakness_branch = self._build_weakness_branch(confidence, keywords)
        if weakness_branch:
            self.root.children.append(weakness_branch)
        
        logger.info("[HierarchicalTree] Built argument tree with %d main branches", len(self.root.children))
        return self.root
    
    def _build_precedent_branch(self, precedents: List[Dict[str, Any]], 
                                keywords: List[Tuple[str, float]]) -> TreeNode:
        """Build precedent alignment branch."""
        if not precedents:
            return None
        
        # Calculate precedent alignment score based on actual similarities (convert from percentage 0-100 to 0-1)
        avg_sim = sum(p.get("similarity", 50.0) / 100.0 for p in precedents) / len(precedents)
        precedent_score = min(0.98, max(0.4, avg_sim))
        
        branch = TreeNode(
            name="Strong Precedent Alignment",
            confidence=precedent_score,
            description="Relevant case precedents supporting the prediction"
        )
        
        # Add precedent evidence
        for i, precedent in enumerate(precedents[:3]):
            case_id = precedent.get("id", f"Case-{i+1}")
            label = precedent.get("label", 1)
            # similarity comes as a percentage from faiss, convert to 0-1
            similarity = precedent.get("similarity", 85.0) / 100.0
            
            # Create child node for each precedent
            precedent_node = TreeNode(
                name=f"{case_id} (Similar: {similarity:.2f})",
                confidence=similarity,
                description=f"Reference case with similar facts and law"
            )
            
            # Add support evidence if outcome matches
            if label == 1:
                precedent_node.evidence = [
                    f"Historical outcome: ACCEPTED",
                    f"Semantic similarity: {similarity:.2%}",
                    f"Applicable precedent range: High"
                ]
            else:
                precedent_node.evidence = [
                    f"Historical outcome: REJECTED",
                    f"Semantic similarity: {similarity:.2%}",
                    f"Counter-precedent analysis required"
                ]
            
            branch.children.append(precedent_node)
        
        # Add keyword evidence
        if keywords:
            key_terms = [f"{kw[0]}" for kw in keywords[:3]]
            branch.evidence = [
                f"Key matching terms: {', '.join(key_terms)}",
                f"Precedent base count: {len(precedents)}"
            ]
        
        return branch
    
    def _build_statutory_branch(self, statutes: List[Dict[str, str]], 
                               reasoning_trail: List[str]) -> TreeNode:
        """Build statutory support branch."""
        if not statutes:
            return None
        
        # Calculate statutory support score based on section relevance
        statute_score = min(0.85, 0.5 + (len(statutes) * 0.1))
        
        branch = TreeNode(
            name="Statutory Support",
            confidence=statute_score,
            description="Applicable legal statutes and provisions"
        )
        
        # Add statute nodes
        for statute in statutes[:3]:
            section = statute.get("section", "Unknown")
            act = statute.get("act", "")
            
            statute_node = TreeNode(
                name=f"Section {section}",
                confidence=0.75,
                description=f"{act}" if act else "Statute provision"
            )
            
            # Extract relevant reasoning trail for this statute
            trail_mentions = [t for t in reasoning_trail if str(section) in t]
            if trail_mentions:
                statute_node.evidence = trail_mentions[:2]
            else:
                statute_node.evidence = [
                    f"Applicable provision for case type",
                    f"Referenced in statutory framework"
                ]
            
            branch.children.append(statute_node)
        
        branch.evidence = [
            f"Statute sections analyzed: {len(statutes)}",
            f"Framework completeness: High"
        ]
        
        return branch
    
    def _build_weakness_branch(self, confidence: float, 
                              keywords: List[Tuple[str, float]]) -> TreeNode:
        """Build weakness/counter-argument analysis branch."""
        
        # Calculate weakness score (inverse of confidence for identified gaps)
        weakness_score = 1.0 - (confidence / 100.0) if confidence <= 100 else 0.15
        
        branch = TreeNode(
            name="Weakness Identified",
            confidence=weakness_score,
            description="Areas where argument is less robust"
        )
        
        # Identify weaknesses based on confidence level
        weakness_factors = []
        
        if confidence < 60:
            weakness_factors.append("Low confidence prediction - Evidence inconclusive")
            weakness_branch_conf = 0.85
        elif confidence < 80:
            weakness_factors.append("Moderate confidence - Some uncertainties remain")
            weakness_branch_conf = 0.65
        else:
            # Check for conflicting or weak keywords
            low_weight_keywords = [kw[0] for kw in keywords if kw[1] < 0.3]
            if low_weight_keywords:
                weakness_factors.append(f"Weak semantic indicators for: {', '.join(low_weight_keywords[:2])}")
                weakness_branch_conf = 0.45
            else:
                weakness_factors.append("Minor factual ambiguities remain unaddressed")
                # Make the weakness confidence inversely proportional to overall confidence
                weakness_branch_conf = max(0.15, round(1.0 - (confidence / 100.0), 2))
        
        # Add weakness nodes
        for i, weakness in enumerate(weakness_factors):
            weakness_node = TreeNode(
                name=f"Gap {i+1}: {weakness.split('-')[0].strip()}",
                confidence=weakness_branch_conf,
                description=weakness
            )
            weakness_node.evidence = [
                "Requires further substantiation",
                "Alternative interpretations possible"
            ]
            branch.children.append(weakness_node)
        
        branch.evidence = [
            f"Confidence level: {confidence:.2f}%",
            f"Identified gaps: {len(weakness_factors)}"
        ]
        
        return branch
    
    def get_tree_summary(self) -> Dict[str, Any]:
        """Get summary of the argument tree."""
        if not self.root:
            return {}
        
        return {
            "outcome": self.outcome,
            "overall_confidence": round(self.overall_confidence * 100, 2),
            "main_arguments": len(self.root.children),
            "total_evidence_points": self._count_evidence_nodes(self.root),
            "tree_depth": self._get_tree_depth(self.root)
        }
    
    def _count_evidence_nodes(self, node: TreeNode) -> int:
        """Count total evidence nodes in tree."""
        count = len(node.evidence)
        for child in node.children:
            count += self._count_evidence_nodes(child)
        return count
    
    def _get_tree_depth(self, node: TreeNode, current_depth: int = 0) -> int:
        """Get maximum depth of tree."""
        if not node.children:
            return current_depth
        return max(self._get_tree_depth(child, current_depth + 1) for child in node.children)
    
    def render_ascii(self) -> str:
        """Render tree as ASCII art."""
        if not self.root:
            return ""
        return self.root.to_ascii_tree()
    
    def render_dict(self) -> Dict[str, Any]:
        """Render tree as dictionary for JSON serialization."""
        if not self.root:
            return {}
        result = self.root.to_dict()
        result["summary"] = self.get_tree_summary()
        return result


def extract_precedent_strength(precedents: List[Dict[str, Any]]) -> Tuple[float, str]:
    """Extract overall precedent alignment strength."""
    if not precedents:
        return 0.0, "No precedents available"
    
    avg_similarity = sum(p.get("similarity", 50.0) / 100.0 for p in precedents) / len(precedents)
    matching_outcomes = sum(1 for p in precedents if p.get("label") == 1)
    
    if avg_similarity > 0.8 and matching_outcomes >= len(precedents) * 0.7:
        # Dynamic high score based on actual similarity instead of hardcoded 0.87
        return max(0.85, min(0.99, avg_similarity + 0.05)), "Strong alignment with favorable precedents"
    elif avg_similarity > 0.7:
        return 0.72, "Moderate alignment with jurisprudence"
    else:
        return 0.45, "Weak precedent foundation"


def extract_statutory_strength(statutes: List[Dict[str, str]]) -> Tuple[float, str]:
    """Extract overall statutory framework strength."""
    if not statutes:
        return 0.0, "No applicable statutes identified"
    
    statute_count = len(statutes)
    
    if statute_count >= 3:
        return 0.72, "Strong statutory framework"
    elif statute_count >= 2:
        return 0.65, "Adequate statutory basis"
    else:
        return 0.50, "Limited statutory support"


def extract_weakness_factors(confidence: float, keywords: List[Tuple[str, float]]) -> List[str]:
    """Extract identified weaknesses from prediction."""
    weaknesses = []
    
    if confidence < 50:
        weaknesses.append("Fundamental uncertainty in legal classification")
    
    if confidence < 70:
        weaknesses.append("Limited factual certainty")
    
    # Check for conflicting keywords
    low_weight_keywords = [kw[0] for kw in keywords if kw[1] < 0.3]
    if low_weight_keywords:
        weaknesses.append(f"Weak indicators: {', '.join(low_weight_keywords[:2])}")
    
    if not weaknesses:
        weaknesses.append("Minor factual ambiguities remain unaddressed")
    
    return weaknesses
