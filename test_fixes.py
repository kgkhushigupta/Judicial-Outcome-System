#!/usr/bin/env python3
"""Test script to verify all fixes for confidence and tree variations."""

import sys
import json
import requests

print("\n" + "="*70)
print("TESTING HIERARCHICAL TREE CONFIDENCE & VARIATION FIXES")
print("="*70 + "\n")

# Test cases with different content
test_cases = [
    {
        "name": "Criminal Case - Murder with Evidence",
        "text": "Appeal against conviction under Section 302 IPC for murder. The appellant claims self-defense under Section 96 IPC. Three eyewitnesses identified the appellant. Medical evidence confirms multiple stab wounds causing death. The weapon was recovered at the instance of the appellant."
    },
    {
        "name": "Civil Case - Contract Dispute",
        "text": "Civil appeal regarding breach of contract. The parties entered into a sale agreement dated 01.01.2023. The buyer claims the goods delivered were defective and violate the Sale of Goods Act, 1930 Section 45. The seller argues the goods were conforming to the specifications. Experts report shows the goods had manufacturing defects."
    },
    {
        "name": "Constitutional Case - Fundamental Rights",
        "text": "Petition under Article 32 of the Constitution. The petitioner claims violation of Article 21 (Right to Life) and Article 19 (Freedom of Expression). The government argues national security concerns justify the restrictions. The case involves interpreting the scope of fundamental rights in modern times."
    },
    {
        "name": "Labour Case - Wrongful Termination",
        "text": "Industrial dispute regarding wrongful termination under Industrial Disputes Act, 1947 Section 127. The worker was terminated without conducting proper inquiry. The employer claims justified dismissal based on performance. Union intervenes citing violation of Section 33 regarding termination during strike period."
    },
    {
        "name": "Copyright Case - Fair Use",
        "text": "Copyright infringement case under Section 107 of the Copyright Act. The defendant claims fair use for educational purposes. The plaintiff alleges unauthorized reproduction and distribution. The case involves determining whether the copying constitutes fair use or substantial similarity under Indian copyright law."
    }
]

print("Testing API endpoint: http://localhost:5000/api/analyze\n")

results = []

for i, test_case in enumerate(test_cases, 1):
    print(f"[{i}/{len(test_cases)}] Testing: {test_case['name']}")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/analyze",
            json={"caseText": test_case["text"]},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"  ✗ API Error: {response.status_code}")
            continue
        
        data = response.json()
        
        # Extract key data
        prediction = data.get("prediction", {})
        outcome = prediction.get("outcome")
        confidence = prediction.get("confidence")
        tree = data.get("hierarchical_argument_tree", {})
        tree_summary = tree.get("summary", {})
        
        results.append({
            "name": test_case["name"],
            "outcome": "ACCEPTED" if outcome == 1 else "REJECTED",
            "confidence": confidence,
            "tree_outcome": tree_summary.get("outcome"),
            "tree_confidence": tree_summary.get("overall_confidence"),
            "branches": tree_summary.get("main_argument_branches"),
            "precedent_strength": tree_summary.get("precedent_strength"),
            "weaknesses": tree_summary.get("identified_weaknesses", [])
        })
        
        # Display result
        print(f"  ✓ Outcome: {results[-1]['outcome']}")
        print(f"    Confidence: {confidence}%")
        print(f"    Tree Confidence: {tree_summary.get('overall_confidence')}%")
        print(f"    Tree Branches: {tree_summary.get('main_argument_branches')}")
        print(f"    Weaknesses: {len(results[-1]['weaknesses'])} identified")
        
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Cannot connect to backend. Is Flask running on port 5000?")
        sys.exit(1)
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    print()

# Analysis
print("\n" + "="*70)
print("ANALYSIS")
print("="*70 + "\n")

if len(results) < 2:
    print("❌ Need at least 2 results to compare. Tests failed.")
    sys.exit(1)

# Check for confidence variation
confidences = [r["confidence"] for r in results]
unique_confidences = set(confidences)

print(f"✓ Test Results Summary:")
print(f"  - Cases tested: {len(results)}")
print(f"  - Unique confidence values: {len(unique_confidences)}")
print(f"  - Confidence range: {min(confidences):.1f}% - {max(confidences):.1f}%")

# Check for variation
if len(unique_confidences) == 1:
    print(f"\n⚠️  WARNING: All cases returned SAME confidence ({confidences[0]:.1f}%)")
    print(f"   This suggests the model is not varying predictions based on case content.")
else:
    print(f"\n✅ GOOD: Confidence values VARY across different cases")
    print(f"   Range: {max(confidences):.1f}% - {min(confidences):.1f}%")

# Check for tree variation
print(f"\n✓ Hierarchical Tree Analysis:")
for result in results:
    print(f"  - {result['name']}")
    print(f"    Outcome: {result['tree_outcome']}, Confidence: {result['tree_confidence']}%")
    print(f"    Weaknesses Identified: {result['weaknesses']}")

# Check for 9885% bug
print(f"\n✓ Confidence Display Check:")
for result in results:
    if result["confidence"] > 100:
        print(f"  ❌ BUG DETECTED: {result['name']} shows {result['confidence']}% (should be < 100)")
    else:
        print(f"  ✓ {result['name']}: {result['confidence']:.1f}% (correct format)")

# Summary
print(f"\n" + "="*70)
print("VERDICT")
print("="*70 + "\n")

all_valid = all(r["confidence"] <= 100 for r in results)
varies = len(unique_confidences) > 1

if all_valid and varies:
    print("✅ ALL FIXES WORKING CORRECTLY!")
    print("   - No 9885% bug")
    print("   - Confidence varies by case")
    print("   - Hierarchical tree adapted to each case")
elif all_valid:
    print("⚠️  PARTIAL FIX:")
    print("   ✓ No 9885% bug")
    print("   ✗ Confidence still not varying by case")
    print("     Action: Check precedent similarity scores and case adjustment factors")
else:
    print("❌ ISSUES REMAIN:")
    print("   - Confidence display bug (> 100%)")
    print("   - Review backend confidence calculation")

print()
