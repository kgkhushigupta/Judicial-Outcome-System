import json
from src.pipeline import run_pipeline

text = "The appellant challenges the High Court's ruling regarding the commercial use of a proprietary software algorithm. The respondent alleges that the appellant extracted and utilized core segments of their copyrighted code in a new commercial analytics product without authorization. The appellant claims the utilization falls under the 'fair use' doctrine and 'transformative use', arguing that the code was substantially modified to serve an entirely different functional purpose not originally intended by the creator. The respondent relies heavily on previous rulings from 2014 which favored strict copyright enforcement over software APIs. However, the appellant points to newer, post-2021 interpretations of digital copyright law that prioritize transformative application and innovation over strict literal enforcement of code structures. The trial court found the appellant liable for infringement, but the appellant has appealed to this bench citing an evolving legal standard in the digital software space."

results = run_pipeline(query_text=text)

print("\n--- PREDICTION ---")
outcome = "ACCEPTED" if results["prediction"]["outcome"] == 1 else "REJECTED"
print("Outcome: " + outcome)
print("Confidence: " + str(results["prediction"]["confidence"]) + "%")

print("\n--- TEMPORAL DRIFT ---")
print(json.dumps(results.get("temporal_drift"), indent=2))

print("\n--- HIERARCHICAL TREE SUMMARY ---")
print(json.dumps(results.get("hierarchical_argument_tree", {}).get("summary"), indent=2))
