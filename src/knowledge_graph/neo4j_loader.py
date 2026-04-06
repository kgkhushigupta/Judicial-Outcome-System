"""
Neo4j Knowledge Graph Loader
Loads and manages judicial knowledge graph in Neo4j
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class Neo4jLoader:
    """Load and manage judicial knowledge graph in Neo4j."""
    
    def __init__(self, uri="bolt://localhost:7687", username="neo4j", password="password", offline_mode=False):

        self.uri = uri
        self.username = username
        self.driver = None
        self.connected = False
        self.offline_mode = offline_mode

        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(uri, auth=(username, password))
            # Test connection
            with driver.session() as session:
                session.run("RETURN 1")
            self.driver = driver
            self.connected = True
            logger.info(f"Connected to Neo4j at {uri}")
        except ImportError:
            logger.warning("neo4j-driver not installed. Running in offline mode.")
        except Exception as e:
            logger.warning(f"Could not connect to Neo4j: {str(e)}. Running in offline mode.")
            if not offline_mode:
                raise
    
    def create_case_node(self, case_id: str, case_data: Dict) -> bool:

        if self.driver is None or not self.connected:
            logger.debug(f"[Offline] Would create case node: {case_id}")
            return True  # Return True for offline mode to not break pipeline

        try:
            query = """
            MERGE (c:Case {id:$case_id})
            SET c.title=$title,
                c.year=$year,
                c.court=$court,
                c.judgment=$judgment
            """

            with self.driver.session() as session:
                session.run(query, case_id=case_id, **case_data)

            logger.info(f"Created case node: {case_id}")
            return True

        except Exception as e:
            logger.error(f"Error creating case node: {str(e)}")
            return False if self.connected else True  # Ignore if already offline
    
    def create_relationship(self, case_id1: str, case_id2: str, relationship_type: str = "SIMILAR_TO") -> bool:

        if self.driver is None or not self.connected:
            logger.debug(f"[Offline] Would create relationship: {case_id1} --{relationship_type}--> {case_id2}")
            return True

        try:
            query = """
            MATCH (c1:Case {id:$case_id1})
            MATCH (c2:Case {id:$case_id2})
            MERGE (c1)-[:SIMILAR_TO]->(c2)
            """

            with self.driver.session() as session:
                session.run(query, case_id1=case_id1, case_id2=case_id2)

            logger.info("Created SIMILAR_TO relationship")
            return True

        except Exception as e:
            logger.error(f"Error creating relationship: {str(e)}")
            return False if self.connected else True
    
    def query_similar_cases(self, case_id: str, limit: int = 5) -> List[Dict]:
        """Query similar cases from knowledge graph"""
        
        if self.driver is None or not self.connected:
            logger.debug(f"[Offline] Would query similar cases for {case_id}")
            return []
        
        try:
            query = """
            MATCH (c1:Case {id:$case_id})-[:SIMILAR_TO]->(c2:Case)
            RETURN c2.id as case_id, c2.title as title
            LIMIT $limit
            """
            
            with self.driver.session() as session:
                results = session.run(query, case_id=case_id, limit=limit)
                return [dict(record) for record in results]
        
        except Exception as e:
            logger.error(f"Error querying similar cases: {str(e)}")
            return []
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")


if __name__ == "__main__":

    print("Testing Neo4j Knowledge Graph Loader...\n")

    loader = Neo4jLoader(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="password",
        offline_mode=True  # Offline mode for testing
    )

    case_data = {
        "title": "Fraud Case Example",
        "year": 2023,
        "court": "Supreme Court",
        "judgment": "Conviction"
    }

    loader.create_case_node("CASE_101", case_data)
    print("Neo4j loader test completed (offline mode)")

    loader.create_case_node("CASE_102", case_data)

    loader.create_relationship(
        "CASE_101",
        "CASE_102",
        "SIMILAR_TO"
    )

    print("Graph nodes and relationship created.")

    loader.close()