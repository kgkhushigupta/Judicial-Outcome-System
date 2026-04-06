import pandas as pd
from neo4j import GraphDatabase

class DatasetLoader:

    def __init__(self):

        self.driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j","password")
        )

    def load_cases(self, filepath):

        df = pd.read_csv(filepath)

        with self.driver.session() as session:

            for index, row in df.iterrows():

                case_id = str(row.get("case_id", f"CASE_{index}"))
                title = str(row.get("title", "Legal Case"))
                court = str(row.get("court", "Unknown Court"))
                year = int(row.get("year", 2020))
                judgment = str(row.get("judgment", "Unknown"))

                query = """
                MERGE (c:Case {id:$case_id})
                SET c.title=$title,
                    c.court=$court,
                    c.year=$year,
                    c.judgment=$judgment
                """

                session.run(
                    query,
                    case_id=case_id,
                    title=title,
                    court=court,
                    year=year,
                    judgment=judgment
                )

        print("Cases loaded successfully")

    def close(self):
        self.driver.close()


if __name__ == "__main__":

    loader = DatasetLoader()

    loader.load_cases(
        "data/legal_dataset.csv"
    )

    loader.close()