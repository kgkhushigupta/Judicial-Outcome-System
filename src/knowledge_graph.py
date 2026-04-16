import json
import os
import logging
import re
import uuid

logger = logging.getLogger(__name__)

NEO4J_AVAILABLE = False
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    logger.warning("[Neo4j] neo4j driver not installed.")


class LegalGraph:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = None
        self.connected = False
        if NEO4J_AVAILABLE:
            try:
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
                self.driver.verify_connectivity()
                self.connected = True
                logger.info("[Neo4j] Connected at %s", uri)
            except Exception as e:
                logger.warning("[Neo4j] Connection failed: %s. Using in-memory graph.", str(e))

        self.local_graph = {"statutes": {}, "cases": {}, "edges": []}

    # -----------------------------
    # STATUTES
    # -----------------------------
    def populate_statutes(self, statutes_path="data/ipc_statutes.json"):
        if not os.path.exists(statutes_path):
            return

        with open(statutes_path, "r", encoding="utf-8") as f:
            statutes = json.load(f)

        if self.connected and self.driver:
            with self.driver.session() as session:
                for s in statutes:
                    session.run(
                        """
                        MERGE (st:Statute {section: $sec})
                        SET st.title=$title,
                            st.description=$desc,
                            st.punishment=$punishment
                        """,
                        sec=s["section"],
                        title=s["title"],
                        desc=s.get("description", ""),
                        punishment=s.get("punishment", "")
                    )

        for s in statutes:
            self.local_graph["statutes"][s["section"]] = s

    # -----------------------------
    # MAIN LOGIC (UPDATED)
    # -----------------------------
    def traverse_reasoning(self, case_facts, statutes_str):
        sections = re.findall(r"Section\s+(\d+[A-Z]?)", statutes_str, re.IGNORECASE)

        statute_details = []
        ipc_path = "data/ipc_statutes.json"

        if os.path.exists(ipc_path):
            with open(ipc_path, "r") as f:
                all_statutes = json.load(f)

            for s in all_statutes:
                if s["section"] in sections:
                    statute_details.append(
                        f"Section {s['section']} IPC - {s['title']}: {s['punishment']}"
                    )

        # -----------------------------
        # 🔥 ADD CASE + RELATIONSHIP TO NEO4J
        # -----------------------------
        case_id = str(uuid.uuid4())

        if self.connected and self.driver:
            with self.driver.session() as session:
                # Create Case node
                session.run(
                    """
                    MERGE (c:Case {id: $id})
                    SET c.text = $text
                    """,
                    id=case_id,
                    text=case_facts
                )

                # Create relationships
                for sec in sections:
                    session.run(
                        """
                        MATCH (c:Case {id: $cid})
                        MERGE (s:Statute {section: $sec})
                        MERGE (c)-[:REFERS_TO]->(s)
                        """,
                        cid=case_id,
                        sec=sec
                    )

        # Store locally too
        self.local_graph["cases"][case_id] = {
            "text": case_facts,
            "sections": sections
        }

        # -----------------------------
        # EXISTING LOGIC (UNCHANGED)
        # -----------------------------
        path = [
            f"Case analysis initiated. Key factual matrix: \"{case_facts[:100]}...\"",
            f"Governing statutes detected: {statutes_str}",
        ]

        for detail in statute_details[:3]:
            path.append(f"Statute provision: {detail}")

        path.extend([
            "Historical precedent vectors retrieved from FAISS index (top-3 cosine similarity).",
            "Factual pattern alignment with precedent outcomes via XGBoost feature weighting.",
            "Final prediction synthesized from statutory, precedent, and factual signals."
        ])

        return path

    # -----------------------------
    # STATS
    # -----------------------------
    def get_graph_stats(self):
        if self.connected and self.driver:
            try:
                with self.driver.session() as session:
                    sc = session.run("MATCH (s:Statute) RETURN count(s) AS c").single()["c"]
                    cc = session.run("MATCH (c:Case) RETURN count(c) AS c").single()["c"]
                    ec = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
                    return {
                        "connected": True,
                        "statutes": sc,
                        "cases": cc,
                        "edges": ec,
                        "backend": "Neo4j"
                    }
            except Exception:
                pass

        return {
            "connected": self.connected,
            "statutes": len(self.local_graph.get("statutes", {})),
            "cases": len(self.local_graph.get("cases", {})),
            "edges": len(self.local_graph.get("edges", [])),
            "backend": "Neo4j" if self.connected else "In-Memory Graph"
        }

    # -----------------------------
    # GRAPH DATA (for UI)
    # -----------------------------
    def get_graph_data(self):
        nodes = []
        edges = []

        for sec, data in self.local_graph.get("statutes", {}).items():
            nodes.append({
                "id": f"statute_{sec}",
                "label": f"S.{sec} IPC",
                "type": "Statute",
                "title": data.get("title", ""),
                "punishment": data.get("punishment", "")
            })

        for cid, data in self.local_graph.get("cases", {}).items():
            nodes.append({
                "id": f"case_{cid}",
                "label": "Case",
                "type": "Case"
            })

            for sec in data.get("sections", []):
                edges.append({
                    "from": f"case_{cid}",
                    "to": f"statute_{sec}",
                    "type": "REFERS_TO"
                })

        return {"nodes": nodes, "edges": edges}

    def close(self):
        if self.driver:
            self.driver.close()