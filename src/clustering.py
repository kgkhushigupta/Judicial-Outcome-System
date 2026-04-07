import numpy as np
import logging
from sklearn.cluster import KMeans, AgglomerativeClustering

logger = logging.getLogger(__name__)

CLUSTER_LABEL_MAP = {
    0: "Criminal Offenses & Penal Law",
    1: "Civil Disputes & Property Law",
    2: "Constitutional & Writ Jurisdiction",
    3: "Family & Matrimonial Law",
    4: "Financial & Commercial Disputes",
    5: "Motor Accident & Compensation Claims"
}


def cluster_embeddings(embeddings, n_clusters=6, method="kmeans"):
    if embeddings is None or len(embeddings) == 0:
        return [], {}

    n_samples = len(embeddings)
    n_clusters = min(n_clusters, n_samples)

    logger.info("[Clustering] Running %s with k=%d on %d samples.", method, n_clusters, n_samples)

    if method == "kmeans":
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)
        labels = model.fit_predict(embeddings)
        inertia = model.inertia_
        logger.info("[Clustering] KMeans inertia: %.4f", inertia)
    elif method == "agglomerative":
        model = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
        labels = model.fit_predict(embeddings)
        logger.info("[Clustering] Agglomerative clustering complete.")
    else:
        model = KMeans(n_clusters=n_clusters, random_state=42)
        labels = model.fit_predict(embeddings)

    cluster_info = {}
    for cid in range(n_clusters):
        mask = labels == cid
        count = int(np.sum(mask))
        cluster_info[cid] = {
            "label": CLUSTER_LABEL_MAP.get(cid, f"Cluster {cid}"),
            "count": count,
            "percentage": round(count / n_samples * 100, 2)
        }

    logger.info("[Clustering] Distribution: %s",
               {v["label"]: v["count"] for v in cluster_info.values()})

    return labels.tolist(), cluster_info


def get_hierarchical_clusters(embeddings, n_clusters_range=(4, 8)):
    """Build a multi-level hierarchy using agglomerative (Ward) clustering."""
    results = {}
    for k in range(n_clusters_range[0], n_clusters_range[1] + 1):
        labels, info = cluster_embeddings(embeddings, n_clusters=k, method="agglomerative")
        results[k] = {"labels": labels, "info": info}
    logger.info("[Clustering] Hierarchical multi-resolution analysis complete (k=%d..%d).",
               n_clusters_range[0], n_clusters_range[1])
    return results
