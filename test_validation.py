import json
import logging
from src.pipeline import run_pipeline

logging.basicConfig(level=logging.INFO)

test_case = "She petitions the court to overturn the lower court's decision regarding her employment termination. She argues that her dismissal was unlawful and violated the terms of her contract. The respondent corporation claims she was terminated for continuous breaches of protocol, but she has provided extensive documentation proving that male colleagues committing identical breaches faced no such penalties. The trial court dismissed her case, stating the corporation acted within its rights, but she has brought the appeal to this bench citing discriminatory practices."

print("\n--- RUNNING FULL PIPELINE TEST ---")
try:
    results = run_pipeline(query_text=test_case)
    
    print("\n[SUCCESS] Pipeline executed without errors.")
    print(f"Outcome: {'ACCEPTED' if results['prediction']['outcome'] == 1 else 'REJECTED'}")
    print(f"Confidence: {results['prediction']['confidence']}%")
    
    if "temporal_drift" in results:
        drift = results["temporal_drift"]
        print(f"\n[Temporal Drift Module] Working. Has drift: {drift.get('has_drift')}")
    else:
        print("\n[ERROR] Temporal Drift data missing!")
        
    if "bias_mitigation_log" in results:
        bias = results["bias_mitigation_log"]
        print(f"\n[Bias Mitigation Module] Working. Applied: {bias.get('applied')}")
        if bias.get("applied"):
            print(f"Reason: {bias.get('reason')}")
    else:
        print("\n[ERROR] Bias Mitigation data missing!")
        
    if "hierarchical_argument_tree" in results:
        tree = results["hierarchical_argument_tree"]
        print(f"\n[Hierarchical Tree Module] Working. Nodes: {len(tree.get('children', []))}")
    else:
        print("\n[ERROR] Hierarchical Tree data missing!")

except Exception as e:
    print(f"\n[FATAL ERROR] Pipeline crashed: {str(e)}")
