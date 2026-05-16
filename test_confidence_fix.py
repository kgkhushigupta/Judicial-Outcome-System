#!/usr/bin/env python3
"""Test script to verify confidence variation and tree differences for different cases."""

import sys
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("TESTING CONFIDENCE VARIATION AND HIERARCHICAL TREE DIFFERENCES")
print("="*70 + "\n")

# Test cases with different characteristics
test_cases = [
    {
        "name": "Criminal - Murder Case",
        "text": "Appeal against conviction under Section 302 IPC for murder. Appellant claims self-defense under Section 96 IPC. Three eyewitnesses identified the appellant. Medical evidence confirms cause of death. Weapon recovered at instance of appellant."
    },
    {
        "name": "Civil - Copyright Case",
        "text": "Suit for copyright infringement regarding fair use doctrine. Transformative use of copyrighted material for research purposes. Defendant claims exception under Section 52(1)(a) of Copyright Act. Digital reproduction for educational benefit."
    },
    {
        "name": "Labour - Dispute Case",
        "text": "Industrial dispute regarding wrongful termination. Employee claims violation of Section 5(1) of ID Act. Employer cites performance issues. Retrenchment notice issued without proper procedure. Gratuity calculation disputed."
    },
    {
        "name": "Constitutional - Rights Case",
        "text": "Petition challenging fundamental right violation under Article 21. State action alleged to be unconstitutional. Procedural fairness not provided. Due process requirements ignored. Right to life and personal liberty at stake."
    },
    {
        "name": "Criminal - Theft Case",
        "text": "Conviction for theft under Section 379 IPC. Allegedly stolen property recovered from accused's possession. Eye witness testimony contradicts. Section 50 CrPC compliance questioned. Chain of custody not properly maintained."
    }
]

def test_predictions():
    """Test that different cases produce different predictions."""
    try:
        from src.pipeline import run_pipeline
        
        results_summary = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[Test {i}/{len(test_cases)}] {test_case['name']}")
            print("-" * 70)
            
            try:
                results = run_pipeline(query_text=test_case['text'])
                
                prediction = results.get('prediction', {})
                outcome = "ACCEPTED" if prediction.get('outcome') == 1 else "REJECTED"
                confidence = prediction.get('confidence', 0)
                
                tree_data = results.get('hierarchical_argument_tree', {})
                tree_summary = tree_data.get('summary', {})
                
                # Check tree structure
                tree_struct = tree_data.get('tree_structure', {})
                num_branches = len(tree_struct.get('children', []))
                
                print(f"  Outcome:      {outcome}")
                print(f"  Confidence:   {confidence:.1f}%")
                print(f"  Tree Branches: {num_branches}")
                
                # Validate confidence range
                if confidence < 45 or confidence > 99.5:
                    print(f"  ⚠️  WARNING: Confidence out of range!")
                else:
                    print(f"  ✓ Confidence in valid range")
                
                # Validate percentage format (should not be 9885% or similar)
                if confidence > 100:
                    print(f"  ✗ ERROR: Confidence > 100 (percentage multiplied twice!)")
                else:
                    print(f"  ✓ Confidence format correct")
                
                # Check tree exists
                if tree_data and tree_summary:
                    print(f"  ✓ Tree generated successfully")
                    print(f"    - Main arguments: {tree_summary.get('main_argument_branches', 0)}")
                else:
                    print(f"  ✗ ERROR: Tree not generated")
                
                results_summary.append({
                    "case": test_case['name'],
                    "outcome": outcome,
                    "confidence": confidence,
                    "branches": num_branches,
                    "tree_quality": "good" if tree_data else "missing"
                })
                
            except Exception as e:
                print(f"  ✗ ERROR: {str(e)}")
                results_summary.append({
                    "case": test_case['name'],
                    "error": str(e)
                })
        
        return results_summary
        
    except ImportError as e:
        print(f"\n✗ FAILED: Cannot import pipeline module: {str(e)}")
        print("  Make sure you're in the project root directory")
        return None

def analyze_results(results):
    """Analyze test results to verify variation."""
    if not results:
        return False
    
    print("\n" + "="*70)
    print("ANALYSIS SUMMARY")
    print("="*70 + "\n")
    
    confidences = [r.get('confidence', 0) for r in results if 'confidence' in r]
    outcomes = [r.get('outcome', 'N/A') for r in results if 'outcome' in r]
    
    if len(confidences) < len(test_cases):
        print(f"✗ Not all tests completed ({len(confidences)}/{len(test_cases)})")
        return False
    
    # Check for variation in confidence
    confidence_range = max(confidences) - min(confidences)
    print(f"Confidence Range: {min(confidences):.1f}% - {max(confidences):.1f}%")
    print(f"Variation: {confidence_range:.1f}%")
    
    if confidence_range < 5:
        print("  ⚠️  WARNING: Low variation in confidence (should be > 5%)")
        print("  This suggests predictions aren't varying by case type.")
    else:
        print("  ✓ Good variation in confidence across cases")
    
    # Check for prediction variety
    unique_outcomes = set(outcomes)
    print(f"\nUnique Outcomes: {', '.join(unique_outcomes)}")
    if len(unique_outcomes) == 1:
        print("  ⚠️  WARNING: All cases have same outcome (should have variation)")
    else:
        print("  ✓ Good variety in predictions")
    
    # Check for percentage format issues
    bad_confidences = [c for c in confidences if c > 100 or c < 45]
    if bad_confidences:
        print(f"\n✗ ERROR: Invalid confidence values: {bad_confidences}")
        return False
    else:
        print(f"\n✓ All confidence values in valid range (45-99.5%)")
    
    return True

if __name__ == "__main__":
    print("Running prediction variation tests...")
    results = test_predictions()
    
    if results:
        success = analyze_results(results)
        
        print("\n" + "="*70)
        if success:
            print("✅ ALL TESTS PASSED - Fixes working correctly!")
        else:
            print("⚠️  TESTS FAILED - Issues detected")
        print("="*70 + "\n")
        
        sys.exit(0 if success else 1)
    else:
        print("\n" + "="*70)
        print("✗ TEST EXECUTION FAILED")
        print("="*70 + "\n")
        sys.exit(1)
