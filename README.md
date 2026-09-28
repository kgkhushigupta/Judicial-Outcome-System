# ⚖️ Judicial AI System — Outcome Predictor & Bias-Aware Legal Analysis

An end-to-end AI platform designed for legal outcome prediction, semantic precedent retrieval, hierarchical argument tree generation, and bias audit across judicial case datasets.

---

## 🚀 Key Features

- **⚖️ Outcome Prediction & Confidence Scoring**: Uses **XGBoost** and **PyTorch** to predict court rulings (`ACCEPTED` / `REJECTED`) along with dynamic confidence adjustments based on precedent strength and statutory alignment.
- **🔍 Semantic Precedent Retrieval**: Implements **FAISS (Facebook AI Similarity Search)** vector indexing with **SentenceTransformers** for high-accuracy similarity search over past case judgments.
- **🌳 Hierarchical Legal Argument Tree**: Constructs structured, case-adapted argument branches mapping precedent strength, relevant statutes, and identified legal weaknesses.
- **🛡️ Fairness & Bias Mitigation**: Integrates **AIF360** and **Fairlearn** to audit demographic parity, equalized odds, and temporal legal drift across judicial data.
- **🕸️ Legal Knowledge Graph**: Links statutory sections (e.g., IPC statutes) using **Neo4j** (with NetworkX fallback).
- **💻 Modern Web Dashboard**: Built with **React 19**, **Vite**, **Tailwind CSS**, and **Lucide Icons** for interactive visual analysis.

---

## 🛠️ Technology Stack

### Backend & AI Pipeline
- **Language**: Python 3.10
- **Framework**: Flask (REST API)
- **Machine Learning & NLP**: PyTorch, spaCy, SentenceTransformers, XGBoost, scikit-learn, PySpark
- **Vector Indexing & Retrieval**: FAISS (cpu)
- **Knowledge Graph**: Neo4j / NetworkX
- **Bias Auditing**: AIF360, Fairlearn

### Frontend
- **Framework**: React 19 + Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide-React / Material Symbols

---

## 📂 Project Structure

```text
Judicial-Bigdata-Project/
├── app.py                      # Flask REST API Server (Port 5000)
├── run_demo.py                 # Terminal CLI runner for pipeline
├── requirements.txt            # Python dependencies
├── src/                        # Core AI & Pipeline logic
│   ├── pipeline.py             # Main inference & prediction engine
│   ├── similarity.py           # FAISS vector similarity search
│   ├── hierarchical_argument_tree.py # Reasoning tree constructor
│   ├── knowledge_graph.py      # Neo4j graph manager
│   ├── bias_detection.py       # Fairness & bias auditing
│   └── temporal_drift.py       # Temporal drift analysis
└── frontend/                   # React 19 + Vite Dashboard UI
    ├── src/pages/              # CasePrediction, CaseUpload, History
    ├── package.json
    └── vite.config.js
```

---

## ⚡ Quick Start & Setup

### 1. Prerequisites
- **Python**: 3.10+
- **Node.js**: v18+ & **npm**

---

### 2. Backend Setup (Flask API)

```bash
# Clone the repository
git clone https://github.com/kgkhushigupta/Judicial-Outcome-System.git
cd Judicial-Outcome-System

# Install Python requirements
pip install -r requirements.txt

# Start the Flask Backend Server
python app.py
```
> **Backend URL**: `http://localhost:5000`

---

### 3. Frontend Setup (React Dashboard)

Open a second terminal window:

```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```
> **Frontend Dashboard URL**: `http://localhost:5173`

---

## 🔌 API Endpoints Summary

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/analyze` | `POST` | Accepts `{ "caseText": "..." }` and returns predictions, FAISS precedents, and reasoning tree |
| `/api/status` | `GET` | System health check (HDFS, Neo4j, PySpark, and NLP modules) |
| `/api/bias` | `GET` | Returns demographic fairness & bias metrics |
| `/api/graph` | `GET` | Returns statute knowledge graph statistics |
| `/api/datasets` | `GET` | Returns status and byte sizes of indexed datasets |

---

## 🧪 Terminal CLI Demo

To execute the analysis pipeline directly in your terminal without starting the web dashboard:

```bash
python run_demo.py
```

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
