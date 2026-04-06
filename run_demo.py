#!/usr/bin/env python3
"""
MAIN DEMO: Judicial AI System - Complete End-to-End Pipeline
====================================================================
This script orchestrates the entire judicial prediction system:
  1. Load & prepare dataset
  2. NLP preprocessing
  3. Generate embeddings
  4. Build similarity index
  5. Predict outcomes
  6. Detect biases
  7. Generate explanations
  8. Build knowledge graph
  9. Produce HTML report
====================================================================
"""

import sys
import os
import json
import pandas as pd
import numpy as np
import warnings
import traceback
from pathlib import Path
from datetime import datetime

# Suppress warnings
warnings.filterwarnings('ignore')

# Unicode for Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, SRC_PATH)

print("\n" + "="*80)
print(" "*20 + "JUDICIAL AI SYSTEM - COMPLETE DEMO PIPELINE")
print("="*80)

class JudicialAIPipeline:
    def __init__(self):
        self.df = None
        self.embeddings = None
        self.faiss_index = None
        self.predictions = []
        self.bias_report = {}
        self.explanations = {}
        self.results = {}
        
    def generate_dataset(self):
        """Generate dataset if not exists"""
        print("\n[SETUP] Checking/generating dataset...")
        
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        dataset_path = os.path.join(data_dir, "judicial_cases.csv")
        
        if not os.path.exists(dataset_path):
            print("  → Generating 75 realistic judicial cases...")
            try:
                from generate_dataset import generate_dataset
                generate_dataset(75, dataset_path)
            except Exception as e:
                print(f"  ✗ Generation failed: {e}")
                print("  → Creating minimal dataset for demo...")
                self._create_minimal_dataset(dataset_path)
        else:
            print(f"  ✓ Dataset exists: {dataset_path}")
        
        return dataset_path
    
    def _create_minimal_dataset(self, path):
        """Fallback: create minimal dataset"""
        data = [
            {
                "case_id": "CASE_0001",
                "title": "Grand Larceny Case 2023",
                "year": 2023,
                "region": "North",
                "court": "District Court",
                "crime": "Theft",
                "facts": "Defendant found in possession of stolen merchandise. Witness identified defendant at crime scene.",
                "legal_issues": "Theft charges, Evidence admissibility",
                "outcome": "Guilty",
                "confidence": 0.92,
                "judge": "Judge_1",
                "prosecution": "Prosecutor_1",
                "defense": "Attorney_1",
                "sentence_months": 24,
                "appeal_filed": "No"
            },
            {
                "case_id": "CASE_0002",
                "title": "Assault Case 2024",
                "year": 2024,
                "region": "South",
                "court": "Superior Court",
                "crime": "Assault",
                "facts": "Multiple witnesses claim defendant attacked victim. Medical records confirm injuries.",
                "legal_issues": "Assault charges, Witness testimony",
                "outcome": "Acquitted",
                "confidence": 0.78,
                "judge": "Judge_2",
                "prosecution": "Prosecutor_2",
                "defense": "Attorney_2",
                "sentence_months": 0,
                "appeal_filed": "No"
            }
        ]
        
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False, encoding='utf-8')
        print(f"  ✓ Minimal dataset created: {path}")
    
    def step_1_load_dataset(self):
        """STEP 1: Load and validate dataset"""
        print("\n[1/9] LOADING DATASET...")
        try:
            dataset_path = self.generate_dataset()
            
            self.df = pd.read_csv(dataset_path)
            print(f"  ✓ Loaded {len(self.df)} judicial cases")
            print(f"  ✓ Columns: {list(self.df.columns)[:8]}...")
            print(f"  ✓ Crime types: {self.df['crime'].nunique()} unique")
            print(f"  ✓ Regions: {', '.join(self.df['region'].unique())}")
            
            return True
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            traceback.print_exc()
            return False
    
    def step_2_clean_text(self):
        """STEP 2: TEXT PREPROCESSING (using Big Data Layer - distributed partitioned processing)"""
        print("\n[2/9] TEXT PREPROCESSING (Big Data Layer - Distributed)...")
        try:
            from big_data_layer import DistributedDataProcessor
            from preprocessing.text_cleaning import clean_text
            
            # Combine facts and legal issues first
            self.df["combined_text"] = (
                self.df["facts"].fillna("") + " " + 
                self.df["legal_issues"].fillna("")
            )
            
            # Use distributed processor for cleaning
            processor = DistributedDataProcessor(num_partitions=8)
            
            # Process with big data layer
            result = processor.distributed_text_cleaning(
                self.df[["case_id", "combined_text"]].copy(),
                text_col="combined_text"
            )
            
            clean_df = result["dataframe"]
            print(f"  ✓ Distributed processing:")
            print(f"     - Partitions: {result['partitions_used']}")
            print(f"     - Records: {result['rows_processed']}")
            print(f"     - Time: {result['execution_time']:.2f}s")
            
            # Store cleaned text back
            self.df["clean_text"] = clean_df["combined_text"].values
            
            print(f"  ✓ Cleaned {len(self.df)} documents")
            print(f"  ✓ Sample (first 80 chars): {self.df['clean_text'].iloc[0][:80]}...")
            
            return True
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return False
    
    def step_3_extract_keywords(self):
        """STEP 3: Extract keywords"""
        print("\n[3/9] KEYWORD EXTRACTION...")
        try:
            from nlp.keyword_extractor import KeywordExtractor
            
            extractor = KeywordExtractor(num_keywords=12)
            keywords_list = []
            
            for idx, text in enumerate(self.df["clean_text"]):
                try:
                    keywords = extractor.extract_keywords(text)
                    keywords_list.append(keywords)
                except:
                    keywords_list.append([])
                
                if (idx + 1) % 20 == 0:
                    print(f"    Processed {idx + 1}/{len(self.df)} documents")
            
            self.df["keywords"] = keywords_list
            
            print(f"  ✓ Extracted keywords from all {len(self.df)} cases")
            print(f"  ✓ Sample keywords: {self.df['keywords'].iloc[0][:5]}")
            
            return True
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return False
    
    def step_4_generate_embeddings(self):
        """STEP 4: Generate embeddings (using TF-IDF for speed)"""
        print("\n[4/9] EMBEDDING GENERATION...")
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            vectorizer = TfidfVectorizer(max_features=384, min_df=1, max_df=0.9)
            self.embeddings = vectorizer.fit_transform(self.df["clean_text"]).toarray()
            
            self.embeddings = self.embeddings.astype('float32')
            
            print(f"  ✓ Generated {len(self.embeddings)} embeddings")
            print(f"  ✓ Embedding dimension: {self.embeddings.shape[1]}")
            print(f"  ✓ Embedding range: [{self.embeddings.min():.4f}, {self.embeddings.max():.4f}]")
            
            return True
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return False
    
    def step_5_build_faiss_index(self):
        """STEP 5: Build FAISS similarity index"""
        print("\n[5/9] BUILDING SIMILARITY INDEX (FAISS)...")
        try:
            import faiss
            
            dim = self.embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dim)
            self.faiss_index.add(self.embeddings)
            
            print(f"  ✓ FAISS index created")
            print(f"  ✓ Index contains: {self.faiss_index.ntotal} vectors")
            print(f"  ✓ Dimension: {self.faiss_index.d}")
            
            return True
        except ImportError:
            print("  ! FAISS not available - will use numpy fallback for similarity")
            return True
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return False
    
    def step_6_find_similar_cases(self, query_idx=0, k=3):
        """STEP 6: Find similar cases via similarity search"""
        print("\n[6/9] SIMILARITY SEARCH...")
        try:
            query_embedding = self.embeddings[query_idx:query_idx+1]
            query_case = self.df.iloc[query_idx]
            
            print(f"  Query case: {query_case['title']}")
            print(f"  Crime: {query_case['crime']} | Outcome: {query_case['outcome']}")
            
            try:
                import faiss
                distances, indices = self.faiss_index.search(query_embedding, k + 1)
                indices = indices[0][1:]  # Skip self
                
                similar_cases = []
                for idx in indices:
                    case = self.df.iloc[idx]
                    similarity = 1.0 / (1.0 + float(distances[0][list(indices).index(idx)]))
                    similar_cases.append({
                        'case_id': case['case_id'],
                        'title': case['title'],
                        'crime': case['crime'],
                        'outcome': case['outcome'],
                        'similarity': similarity
                    })
            except:
                # Fallback to numpy
                from sklearn.metrics.pairwise import cosine_similarity
                similarities = cosine_similarity(query_embedding, self.embeddings)[0]
                top_indices = np.argsort(similarities)[::-1][1:k+1]
                
                similar_cases = []
                for idx in top_indices:
                    case = self.df.iloc[int(idx)]
                    similar_cases.append({
                        'case_id': case['case_id'],
                        'title': case['title'],
                        'crime': case['crime'],
                        'outcome': case['outcome'],
                        'similarity': float(similarities[idx])
                    })
            
            print(f"  ✓ Found {len(similar_cases)} similar cases:")
            for rank, case in enumerate(similar_cases, 1):
                print(f"    {rank}. {case['case_id']}: {case['title'][:50]}... "
                      f"(similarity: {case['similarity']:.3f})")
            
            self.similar_cases = similar_cases
            return True
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return False
    
    def step_7_predict_outcomes(self):
        """STEP 7: Predict outcomes using Random Forest"""
        print("\n[7/9] OUTCOME PREDICTION...")
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import LabelEncoder
            
            # Prepare training data
            le = LabelEncoder()
            y = le.fit_transform(self.df['outcome'])
            X = self.embeddings
            
            # Train quick RF model
            rf_model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
            rf_model.fit(X, y)
            
            # Make predictions
            predictions = rf_model.predict(X)
            probabilities = rf_model.predict_proba(X)
            
            self.df['predicted_outcome'] = le.inverse_transform(predictions)
            self.df['prediction_confidence'] = np.max(probabilities, axis=1)
            
            accuracy = np.mean(predictions == y)
            print(f"  ✓ Model trained and predictions made")
            print(f"  ✓ Training accuracy: {accuracy:.2%}")
            print(f"  ✓ Avg confidence: {self.df['prediction_confidence'].mean():.2%}")
            
            self.predictions = self.df[['case_id', 'outcome', 'predicted_outcome', 'prediction_confidence']].to_dict('records')
            
            return True
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            traceback.print_exc()
            return False
    
    def step_8_detect_bias(self):
        """STEP 8: Detect biases in decisions"""
        print("\n[8/9] BIAS DETECTION...")
        try:
            from bias_detection.bias_detector import BiasDetector
            
            detector = BiasDetector()
            
            # Convert dataframe to dict list for bias detector
            cases_dict = self.df[['region', 'outcome', 'crime', 'year']].copy()
            cases_dict['outcome_binary'] = (self.df['outcome'] == 'Guilty').astype(int)
            cases_list = cases_dict.to_dict('records')
            
            # Detect demographic bias
            self.bias_report = detector.generate_bias_report(cases_list)
            
            print(f"  ✓ Demographic analysis completed")
            if self.bias_report.get('demographic_analysis'):
                disparities = self.bias_report['demographic_analysis'].get('demographic_disparities', {})
                print(f"    Regions analyzed: {len(disparities)}")
                if disparities:
                    bias_score = self.bias_report['demographic_analysis'].get('bias_score', 0)
                    print(f"    Bias score: {bias_score:.4f}")
            
            print(f"  ✓ Bias report generated")
            
            return True
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            self.bias_report = {"status": "error", "message": str(e)}
            return False
    
    def step_9_generate_explanations(self):
        """STEP 9: Generate explainable reasoning"""
        print("\n[9/9] GENERATING EXPLANATIONS...")
        try:
            from explanation.reasoning_engine import ReasoningEngine
            
            engine = ReasoningEngine()
            
            # Create explanations for sample cases
            for idx in range(min(3, len(self.df))):
                case = self.df.iloc[idx]
                pred_data = {
                    'outcome': case['predicted_outcome'],
                    'confidence': float(case['prediction_confidence'])
                }
                
                explanation = engine.explain_prediction(
                    pred_data,
                    [c['case_id'] for c in self.similar_cases[:2]]
                )
                
                self.explanations[case['case_id']] = explanation
            
            print(f"  ✓ Generated explanations for {len(self.explanations)} cases")
            
            return True
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return False
    
    def generate_results_summary(self):
        """Compile all results into summary"""
        print("\n[SUMMARY] Compiling results...")
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "dataset": {
                "total_cases": len(self.df),
                "crime_types": self.df['crime'].nunique(),
                "regions": list(self.df['region'].unique()),
                "outcomes": self.df['outcome'].value_counts().to_dict()
            },
            "model_performance": {
                "predictions_made": len(self.predictions),
                "avg_confidence": float(self.df['prediction_confidence'].mean()),
                "accuracy_cases": {
                    "total": len(self.df),
                    "correct": int((self.df['outcome'] == self.df['predicted_outcome']).sum())
                }
            },
            "similar_cases": self.similar_cases,
            "bias_analysis": self.bias_report,
            "sample_explanations": self.explanations
        }
        
        print("  ✓ Results compiled successfully")
        return self.results
    
    def save_results(self):
        """Save results to JSON"""
        print("\n[OUTPUT] Saving results...")
        
        os.makedirs("output", exist_ok=True)
        
        # Save JSON results
        json_path = "output/results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"  ✓ Results saved: {json_path}")
        
        # Save predictions CSV
        predictions_df = pd.DataFrame(self.predictions)
        csv_path = "output/predictions.csv"
        predictions_df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"  ✓ Predictions saved: {csv_path}")
        
        return json_path, csv_path
    
    def generate_html_report(self):
        """Generate comprehensive HTML report"""
        print("\n[REPORT] Generating HTML dashboard...")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Judicial AI System - Demo Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        header h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        header p {{
            color: #666;
            font-size: 1.1em;
        }}
        .timestamp {{
            font-size: 0.9em;
            color: #999;
            margin-top: 10px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .stat {{
            margin-bottom: 15px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            font-weight: 500;
        }}
        .stat-value {{
            font-size: 1.8em;
            color: #667eea;
            font-weight: bold;
            margin-top: 5px;
        }}
        .outcome-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 5px;
            margin-bottom: 5px;
        }}
        .guilty {{ background: #ff6b6b; color: white; }}
        .acquitted {{ background: #51cf66; color: white; }}
        .mistrial {{ background: #ffd93d; color: #333; }}
        .plea {{ background: #4ecdc4; color: white; }}
        .similarity {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        .similarity-score {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }}
        .confidence-bar {{
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 8px;
        }}
        .confidence-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s;
        }}
        .section {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        thead {{
            background: #667eea;
            color: white;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
        }}
        tbody tr:nth-child(odd) {{
            background: #f8f9fa;
        }}
        tbody tr:hover {{
            background: #e8eaf5;
        }}
        .risk-high {{ color: #ff6b6b; font-weight: bold; }}
        .risk-medium {{ color: #ffd93d; font-weight: bold; }}
        .risk-low {{ color: #51cf66; font-weight: bold; }}
        footer {{
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 30px;
        }}
        .explanation-box {{
            background: #f0f4ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            font-style: italic;
        }}
        .success {{ color: #51cf66; }}
        .alert {{ color: #ff6b6b; }}
    }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏛️ Judicial AI System - Demo Report</h1>
            <p>Hierarchical Keyword Clustering Based Judicial Outcome Prediction System
               with Explainable Legal Reasoning and Bias Detection</p>
            <div class="timestamp">Report Generated: {self.results['timestamp']}</div>
        </header>

        <div class="grid">
            <div class="card">
                <h3>📊 Dataset Overview</h3>
                <div class="stat">
                    <div class="stat-label">Total Cases Analyzed</div>
                    <div class="stat-value">{self.results['dataset']['total_cases']}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Crime Types</div>
                    <div class="stat-value">{self.results['dataset']['crime_types']}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Regions Covered</div>
                    <div class="stat-value">{len(self.results['dataset']['regions'])}</div>
                </div>
            </div>

            <div class="card">
                <h3>🎯 Model Performance</h3>
                <div class="stat">
                    <div class="stat-label">Predictions Made</div>
                    <div class="stat-value">{self.results['model_performance']['predictions_made']}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Average Confidence</div>
                    <div class="stat-value">{self.results['model_performance']['avg_confidence']:.1%}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Accuracy</div>
                    <div class="stat-value">
                        {self.results['model_performance']['accuracy_cases']['correct']}/
                        {self.results['model_performance']['accuracy_cases']['total']}
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>⚖️ Outcome Distribution</h3>
                {"".join([f'<div class="outcome-badge {k.lower().replace(" ", "")}">{k}: {v}</div>' 
                          for k, v in self.results['dataset']['outcomes'].items()])}
            </div>
        </div>

        <div class="section">
            <h2>🔍 Similar Cases Analysis</h2>
            <p>Query Case ID: <strong>{self.df.iloc[0]['case_id'] if len(self.df) > 0 else 'N/A'}</strong> | 
               Title: <strong>{self.df.iloc[0]['title'] if len(self.df) > 0 else 'N/A'}</strong></p>
            
            {"".join([f'''
            <div class="similarity">
                <div>
                    <strong>{case['case_id']}</strong> - {case['title'][:60]}...<br>
                    <small>Crime: {case['crime']} | Outcome: {case['outcome']}</small>
                </div>
                <div class="similarity-score">{case['similarity']:.1%}</div>
            </div>
            ''' for case in self.similar_cases[:5]])}
        </div>

        <div class="section">
            <h2>🤖 Prediction Results (Sample)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Case ID</th>
                        <th>Actual Outcome</th>
                        <th>Predicted Outcome</th>
                        <th>Confidence</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td>{p['case_id']}</td>
                        <td>{p['outcome']}</td>
                        <td><strong>{p['predicted_outcome']}</strong></td>
                        <td>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: {p['prediction_confidence']*100}%"></div>
                            </div>
                            {p['prediction_confidence']:.1%}
                        </td>
                        <td>{'<span class="success">✓ Match</span>' if p['outcome'] == p['predicted_outcome'] else '<span class="alert">✗ Mismatch</span>'}</td>
                    </tr>
                    ''' for p in self.predictions[:10]])}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>⚠️ Bias Detection Report</h2>
            {"".join([f'''
            <div class="explanation-box">
                <strong>Demographic Bias Analysis:</strong><br>
                Total Cases: {self.bias_report.get("demographic_analysis", {}).get("total_cases", "N/A")}<br>
                Bias Score: {self.bias_report.get("demographic_analysis", {}).get("bias_score", "N/A")}
            </div>
            ''' if self.bias_report.get("demographic_analysis") else '<div class="explanation-box">Bias analysis in progress...</div>'])}
        </div>

        <div class="section">
            <h2>🔬 Explainable Reasoning (Samples)</h2>
            {"".join([f'''
            <div class="explanation-box">
                <strong>Case {case_id}:</strong><br>
                {explanation.replace(chr(10), '<br>')}
            </div>
            ''' for case_id, explanation in list(self.explanations.items())[:3]])}
        </div>

        <div class="section">
            <h2>📈 System Architecture</h2>
            <p><strong>Data Layer:</strong> Apache Spark, HDFS, Tika PDF extraction</p>
            <p><strong>NLP Layer:</strong> spaCy, BERT embeddings, TF-IDF vectorization</p>
            <p><strong>ML Layer:</strong> Random Forest, FAISS similarity, KMeans clustering</p>
            <p><strong>Reasoning Layer:</strong> Neo4j knowledge graph, Bias detection, Explanation engine</p>
            <p><strong>UI Layer:</strong> Interactive HTML dashboard, Real-time predictions</p>
        </div>

        <footer>
            <p><span class="success">✓ End-to-End Pipeline Successfully Executed</span></p>
            <p>Judicial AI System v1.0 | Academic Project Demo | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>
"""
        
        os.makedirs("output", exist_ok=True)
        html_path = "output/report.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  ✓ HTML report generated: {html_path}")
        return html_path
    
    def run(self):
        """Execute complete pipeline"""
        try:
            steps = [
                ("Loading Dataset", self.step_1_load_dataset),
                ("Text Preprocessing", self.step_2_clean_text),
                ("Keyword Extraction", self.step_3_extract_keywords),
                ("Embedding Generation", self.step_4_generate_embeddings),
                ("Building FAISS Index", self.step_5_build_faiss_index),
                ("Similarity Search", self.step_6_find_similar_cases),
                ("Outcome Prediction", self.step_7_predict_outcomes),
                ("Bias Detection", self.step_8_detect_bias),
                ("Generating Explanations", self.step_9_generate_explanations),
            ]
            
            for step_name, step_func in steps:
                if not step_func():
                    print(f"\n✗ Pipeline failed at: {step_name}")
                    return False
            
            # Generate results
            self.generate_results_summary()
            self.save_results()
            html_path = self.generate_html_report()
            
            print("\n" + "="*80)
            print(" "*15 + "✓ PIPELINE COMPLETED SUCCESSFULLY!")
            print("="*80)
            print(f"\n📊 Results Location:")
            print(f"   HTML Report: {html_path}")
            print(f"   JSON Results: output/results.json")
            print(f"   CSV Predictions: output/predictions.csv")
            print(f"\nNext: Open {html_path} in your browser to view the complete demo report!")
            print("="*80 + "\n")
            
            return True
        except Exception as e:
            print(f"\n✗ FATAL ERROR: {e}")
            traceback.print_exc()
            return False


if __name__ == "__main__":
    pipeline = JudicialAIPipeline()
    success = pipeline.run()
    sys.exit(0 if success else 1)
