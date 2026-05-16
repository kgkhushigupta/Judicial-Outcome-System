#!/usr/bin/env python3
"""Quick validation script to check for import/syntax errors."""

import sys
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

print("\n" + "="*60)
print("VALIDATING HIERARCHICAL TREE IMPLEMENTATION")
print("="*60 + "\n")

try:
    print("[1/5] Importing hierarchical_argument_tree module...")
    from src.hierarchical_argument_tree import (
        TreeNode,
        HierarchicalArgumentTreeBuilder,
        extract_precedent_strength,
        extract_statutory_strength,
        extract_weakness_factors
    )
    print("✓ hierarchical_argument_tree imported successfully\n")
except Exception as e:
    print(f"✗ FAILED: {str(e)}\n")
    sys.exit(1)

try:
    print("[2/5] Importing reasoning module...")
    from src.reasoning import generate_hierarchical_argument_tree
    print("✓ reasoning module imported successfully\n")
except Exception as e:
    print(f"✗ FAILED: {str(e)}\n")
    sys.exit(1)

try:
    print("[3/5] Importing preprocess module...")
    from src.preprocess import process_batch_spark, process_text, process_entities, get_nlp_status
    print("✓ preprocess module imported successfully\n")
except Exception as e:
    print(f"✗ FAILED: {str(e)}\n")
    sys.exit(1)

try:
    print("[4/5] Testing TreeNode creation...")
    test_node = TreeNode(
        name="Test Node",
        confidence=0.85,
        description="Test description",
        evidence=["Evidence 1", "Evidence 2"]
    )
    print(f"✓ TreeNode created: {test_node.name} (confidence: {test_node.confidence})\n")
except Exception as e:
    print(f"✗ FAILED: {str(e)}\n")
    sys.exit(1)

try:
    print("[5/5] Testing HierarchicalArgumentTreeBuilder...")
    builder = HierarchicalArgumentTreeBuilder()
    tree = builder.build(
        prediction=1,
        confidence=87.5,
        precedents=[
            {"id": "Case-1", "similarity": 0.89, "label": 1},
            {"id": "Case-2", "similarity": 0.85, "label": 1}
        ],
        statutes=[
            {"section": "107", "act": "Copyright Act"},
            {"section": "52(1)(a)", "act": "Indian Copyright Act"}
        ],
        keywords=[("fair use", 0.92), ("copyright", 0.88)],
        reasoning_trail=["Precedent analysis complete", "Statutory framework evaluated"]
    )
    print(f"✓ Tree built successfully")
    print(f"  - Root: {tree.name}")
    print(f"  - Children: {len(tree.children)}")
    print(f"  - Overall Confidence: {builder.overall_confidence:.2f}\n")
except Exception as e:
    print(f"✗ FAILED: {str(e)}\n")
    sys.exit(1)

print("="*60)
print("✅ ALL VALIDATIONS PASSED!")
print("="*60)
print("\nThe hierarchical tree implementation is ready to use.")
print("Start Flask backend with: python app.py")
print("Or run tests with the provided testing guide.\n")
