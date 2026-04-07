import os
import json
from src.pipeline import run_pipeline

def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    print("\n" + "=" * 70)
    print(" JUDICIAL AI OUTCOME PREDICTOR & BIAS-AWARE ANALYSIS ".center(70))
    print(" Hierarchical Semantic Vector Clustering | Apache Spark ".center(70))
    print("=" * 70 + "\n")

    results = run_pipeline()

    print("\n" + "=" * 70)
    print(" ANALYSIS RESULTS ".center(70, "="))
    print("=" * 70)
    print(f"  Case ID        : {results['case_id']}")
    print(f"  Title          : {results['title']}")
    print(f"  Cluster        : {results.get('cluster_info', {}).get('0', {}).get('label', 'N/A')}\n")

    print("─── TOP KEYWORDS (TF-IDF) ───")
    for kw, score in results['top_keywords']:
        print(f"  • {kw.ljust(25)} : {score}")

    print("\n─── CASE SECTIONS DETECTED ───")
    for section, content in results.get('sections', {}).items():
        display = str(content)[:80] + "..." if len(str(content)) > 80 else str(content)
        if display:
            print(f"  [{section}] {display}")

    print("\n─── PRECEDENT RETRIEVAL (FAISS) ───")
    for i, p in enumerate(results['similar_precedents'], start=1):
        label_str = "Accepted" if p.get('label') == 1 else "Rejected"
        print(f"  {i}. Case #{p['id']} — Similarity: {p['similarity']}% (Outcome: {label_str})")

    print("\n─── XGBOOST OUTCOME PREDICTION ───")
    decision = "ACCEPTED" if results['prediction']['outcome'] == 1 else "REJECTED"
    print(f"  Outcome        : {decision}")
    print(f"  Confidence     : {results['prediction']['confidence'] * 100:.2f}%")

    print("\n─── FEATURE IMPORTANCES ───")
    for feat, gain in results['feature_importance'][:5]:
        print(f"  • {feat.ljust(30)} : {gain:.4f}")

    print("\n─── FAIRNESS & BIAS METRICS (AIF360/Fairlearn) ───")
    for k, v in results['bias_report'].items():
        if not k.endswith("_rates"):
            print(f"  {k.ljust(40)} : {v}")

    print("\n─── LEGAL REASONING TRAIL (Neo4j) ───")
    for i, step in enumerate(results['reasoning_trail'], start=1):
        print(f"  {i}. {step}")

    print("\n─── NLG EXPLANATION (Judge-Readable) ───")
    print(f"  {results['explanation']}\n")

    print("─── SYSTEM STATUS ───")
    status = results.get('system_status', {})
    hdfs = status.get('hdfs', {})
    print(f"  HDFS      : {hdfs.get('storage_mode', 'N/A')}")
    print(f"  Neo4j     : {status.get('graph', {}).get('backend', 'N/A')}")
    nlp_s = status.get('nlp', {})
    print(f"  NLP       : {nlp_s.get('processing_mode', 'N/A')}")
    print(f"  FAISS     : {status.get('faiss', {}).get('index_size', 0)} vectors indexed")
    print(f"  Build Time: {status.get('pipeline_build_time', 'N/A')}s")

    print("\n" + "=" * 70)
    print(" Output saved to: output/results.json ".center(70))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
