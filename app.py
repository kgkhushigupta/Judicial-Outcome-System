import os
import sys
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print(" JUDICIAL AI SYSTEM — Initializing Backend Services")
print("=" * 60)
print("[*] Loading ML pipeline (PyTorch, spaCy, SentenceTransformer)...")
print("[*] This may take 15-30 seconds on first run...")

from src.pipeline import run_pipeline, _get_or_build_pipeline
from src.hdfs_manager import HDFSManager
from src.preprocess import get_nlp_status
from src.knowledge_graph import LegalGraph

app = Flask(__name__)
CORS(app)


@app.route('/api/analyze', methods=['POST'])
def analyze_case():
    data = request.json
    if not data or 'caseText' not in data:
        return jsonify({"error": "Missing caseText"}), 400
    case_text = data['caseText']
    logger.info("[API] Received case: %s...", case_text[:60])
    try:
        results = run_pipeline(query_text=case_text)
        return jsonify(results)
    except Exception as e:
        logger.error("[API] Error: %s", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/api/status', methods=['GET'])
def system_status():
    hdfs = HDFSManager()
    graph = LegalGraph()
    nlp = get_nlp_status()
    status = {
        "server": "running",
        "hdfs": hdfs.get_status(),
        "neo4j": graph.get_graph_stats(),
        "nlp": nlp,
        "spark": {"available": nlp.get("spark_available", False)},
        "pipeline_ready": "model" in _get_or_build_pipeline() if False else True
    }
    graph.close()
    return jsonify(status)


@app.route('/api/datasets', methods=['GET'])
def dataset_info():
    datasets = {}
    paths = {
        "ildc": "data/raw/ildc.csv",
        "ddl": "data/raw/ddl.csv",
        "hc": "data/raw/hc.csv",
        "ltc": "data/raw/ltc.csv",
        "ipc": "data/ipc_statutes.json"
    }
    for name, path in paths.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            datasets[name] = {"path": path, "size_bytes": size, "exists": True}
        else:
            datasets[name] = {"path": path, "exists": False}
    return jsonify(datasets)


@app.route('/api/bias', methods=['GET'])
def bias_report():
    try:
        import pandas as pd
        from src.bias_detection import run_bias_analysis
        df = pd.read_csv("data/raw/ddl.csv")
        report = run_bias_analysis(df)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/graph', methods=['GET'])
def graph_data():
    graph = LegalGraph()
    graph.populate_statutes("data/ipc_statutes.json")
    stats = graph.get_graph_stats()
    data = graph.get_graph_data()
    graph.close()
    return jsonify({"stats": stats, "data": data})


if __name__ == '__main__':
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    print("=" * 60)
    print(" Judicial AI System — API Server on http://localhost:5000")
    print("=" * 60)
    app.run(debug=False, port=5000, host="0.0.0.0")
