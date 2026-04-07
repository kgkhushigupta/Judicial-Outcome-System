import json
import os
import time
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from src.hdfs_manager import HDFSManager
from src.load_datasets import load_all_datasets
from src.preprocess import process_text, process_entities, get_nlp_status, process_batch_spark
from src.section_detector import detect_sections, extract_statute_codes
from src.keyword_extractor import extract_keywords
from src.embeddings import LegalEmbedder
from src.clustering import cluster_embeddings, get_hierarchical_clusters, CLUSTER_LABEL_MAP
from src.similarity import FAISSIndex
from src.predictor import train_predictor, predict_outcome
from src.knowledge_graph import LegalGraph
from src.reasoning import generate_explanation, generate_structured_reasoning
from src.bias_detection import run_bias_analysis

_pipeline_cache = {}

def _get_or_build_pipeline(sample_size=500):
    if "model" in _pipeline_cache:
        logger.info("[Pipeline] Using cached pipeline components.")
        return _pipeline_cache

    t0 = time.time()
    hdfs = HDFSManager()

    logger.info("[1/10] Loading datasets...")
    load_all_datasets(hdfs, sample_size=sample_size)

    logger.info("[2/10] Reading ILDC data...")
    df_ildc = pd.read_csv("data/raw/ildc.csv")
    texts = df_ildc["text"].astype(str).tolist()
    labels = df_ildc["label"].tolist()

    logger.info("[3/10] Running Apache Spark NLP preprocessing on corpus...")
    spark_processed = process_batch_spark(texts, labels)
    logger.info("[Spark] Preprocessed %d documents. Avg token count: %.1f",
               len(spark_processed),
               sum(p['token_count'] for p in spark_processed) / max(len(spark_processed), 1))

    logger.info("[4/10] Extracting keywords (TF-IDF)...")
    all_keywords = extract_keywords(texts)

    logger.info("[5/10] Generating embeddings (InLegalBERT)...")
    embedder = LegalEmbedder("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = embedder.encode(texts)

    logger.info("[6/10] Hierarchical clustering of legal concepts (Agglomerative, k=6)...")
    cluster_labels, cluster_info = cluster_embeddings(embeddings, n_clusters=6, method="agglomerative")

    logger.info("[6.5/10] Building multi-level cluster hierarchy (k=4..8)...")
    hierarchical_results = get_hierarchical_clusters(embeddings, n_clusters_range=(4, 8))

    logger.info("[7/10] Building FAISS index...")
    faiss_idx = FAISSIndex(dim=embeddings.shape[1])
    metadata = [{"id": i, "label": int(l), "text_preview": texts[i][:100]} for i, l in enumerate(labels)]
    faiss_idx.build(embeddings, metadata)

    logger.info("[8/10] Training XGBoost predictor...")
    model, features = train_predictor(embeddings, labels)

    logger.info("[9/10] Running bias analysis on DDL dataset...")
    df_ddl = pd.read_csv("data/raw/ddl.csv")
    bias_report = run_bias_analysis(df_ddl)

    logger.info("[9.5/10] Populating knowledge graph...")
    graph = LegalGraph()
    graph.populate_statutes("data/ipc_statutes.json")

    elapsed = round(time.time() - t0, 2)
    logger.info("[10/10] Pipeline built in %.2f seconds.", elapsed)

    _pipeline_cache.update({
        "hdfs": hdfs, "embedder": embedder, "faiss_idx": faiss_idx,
        "model": model, "features": features, "bias_report": bias_report,
        "graph": graph, "cluster_labels": cluster_labels, "cluster_info": cluster_info,
        "hierarchical_results": hierarchical_results, "spark_processed": spark_processed,
        "texts": texts, "labels": labels, "all_keywords": all_keywords,
        "build_time": elapsed
    })
    return _pipeline_cache


def run_pipeline(query_text=None, spark_session=None):
    cache = _get_or_build_pipeline()
    embedder = cache["embedder"]
    faiss_idx = cache["faiss_idx"]
    model = cache["model"]
    features = cache["features"]
    bias_report = cache["bias_report"]
    graph = cache["graph"]
    cluster_info = cache["cluster_info"]

    if not query_text:
        query_text = (
            "The appeal is directed against the judgment and order dated 15.03.2023 passed by "
            "the High Court of Delhi in Criminal Appeal No. 482/2022 whereby the High Court "
            "confirmed the conviction of the appellant under Section 302 of the Indian Penal Code "
            "for the murder of the deceased Ramesh Kumar. The prosecution case is that on the night "
            "of 12.08.2021, the appellant attacked the deceased with a sharp-edged weapon following "
            "a property dispute. Section 302 IPC prescribes punishment of death or imprisonment for "
            "life. The appellant argues self-defense under Section 96 IPC and challenges the "
            "reliability of eyewitness testimony. Three eyewitnesses including PW-1 and PW-2 "
            "identified the appellant. The medical evidence confirms cause of death as hemorrhagic "
            "shock due to multiple stab wounds. The weapon was recovered at the instance of the "
            "appellant under Section 27 of the Indian Evidence Act."
        )

    sections = detect_sections(query_text)
    statute_codes = extract_statute_codes(query_text)
    nlp_tokens = process_text(query_text)
    entities = process_entities(query_text)

    query_emb = embedder.encode([query_text])[0]
    top_precedents = faiss_idx.search(query_emb, top_k=3)
    pred_label, conf = predict_outcome(model, query_emb)
    qt_kws = extract_keywords([query_text])[0]

    statutes_str = ", ".join([f"Section {sc['section']} {sc['act']}" for sc in statute_codes]) if statute_codes else "Section 302 IPC"
    trail = graph.traverse_reasoning(query_text, statutes_str)
    explanation = generate_explanation(trail, pred_label)
    structured = generate_structured_reasoning(trail, pred_label, conf, qt_kws, top_precedents)

    results = {
        "case_id": "QUERY_" + str(int(time.time())),
        "title": "State vs. Appellant (Criminal Appeal)",
        "query_text": query_text[:500],
        "sections": sections,
        "statute_codes": statute_codes,
        "nlp_tokens": nlp_tokens[:30],
        "entities": entities[:15],
        "top_keywords": qt_kws,
        "cluster_assignment": int(cluster_info.get(0, {}).get("count", 0)),
        "cluster_info": {str(k): v for k, v in cluster_info.items()},
        "hierarchical_clustering": {str(k): v["info"] for k, v in cache.get("hierarchical_results", {}).items()},
        "similar_precedents": top_precedents,
        "prediction": {"outcome": int(pred_label), "confidence": float(conf)},
        "feature_importance": features,
        "bias_report": bias_report,
        "reasoning_trail": trail,
        "structured_reasoning": structured,
        "explanation": explanation,
        "system_status": {
            "hdfs": cache["hdfs"].get_status(),
            "graph": graph.get_graph_stats(),
            "faiss": faiss_idx.get_index_info(),
            "embedder": embedder.get_model_info(),
            "nlp": get_nlp_status(),
            "spark": {
                "documents_processed": len(cache.get("spark_processed", [])),
                "processing_mode": get_nlp_status().get("processing_mode", "N/A"),
                "spark_available": get_nlp_status().get("spark_available", False)
            },
            "pipeline_build_time": cache["build_time"]
        }
    }

    os.makedirs("output", exist_ok=True)
    with open("output/results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    return results
