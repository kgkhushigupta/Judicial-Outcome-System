"""
Graph Queries Module
Query utilities for Neo4j knowledge graph
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class GraphQueries:
    """Execute queries on the judicial knowledge graph."""
    
    def __init__(self, neo4j_session):
        """
        Initialize graph queries.
        
        Args:
            neo4j_session: Active Neo4j session
        """
        self.session = neo4j_session
        logger.info("GraphQueries initialized")
    
    def find_related_cases(self, case_id: str, max_depth: int = 2) -> List[Dict]:
        """
        Find cases related to given case.
        
        Args:
            case_id: Case identifier
            max_depth: Maximum depth of relationships to traverse
            
        Returns:
            List of related cases
        """
        if self.session is None:
            return []
        
        try:
            query = f"""
            MATCH (c:Case {{id: $case_id}})-[r*..{max_depth}]-(related:Case)
            RETURN related.id as case_id, related.title as title
            LIMIT 20
            """
            result = self.session.run(query, case_id=case_id)
            return [dict(record) for record in result]
        
        except Exception as e:
            logger.error(f"Error finding related cases: {str(e)}")
            return []
    
    def find_precedents(self, case_id: str) -> List[str]:
        """
        Find precedent cases.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of precedent case IDs
        """
        if self.session is None:
            return []
        
        try:
            query = """
            MATCH (c:Case {id: $case_id})-[:CITES_AS_PRECEDENT]->(precedent:Case)
            RETURN precedent.id as case_id
            """
            result = self.session.run(query, case_id=case_id)
            return [record['case_id'] for record in result]
        
        except Exception as e:
            logger.error(f"Error finding precedents: {str(e)}")
            return []
    
    def get_case_info(self, case_id: str) -> Optional[Dict]:
        """
        Get detailed information about a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Case information dictionary
        """
        if self.session is None:
            return None
        
        try:
            query = """
            MATCH (c:Case {id: $case_id})
            RETURN c as case_info
            """
            result = self.session.run(query, case_id=case_id)
            record = result.single()
            
            if record:
                return dict(record['case_info'])
            return None
        
        except Exception as e:
            logger.error(f"Error getting case info: {str(e)}")
            return None


if __name__ == "__main__":
    # Usage example would go here
    pass
