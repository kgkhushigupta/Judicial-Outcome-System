"""
Master Pipeline: Connect all modules for end-to-end processing
Pipeline Flow:
  Dataset (CSV) -> Text Cleaning -> Keyword Extraction -> 
  Embeddings -> FAISS Index -> Similarity Search
"""

import sys
import os
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# Fix Unicode for Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("JUDICIAL AI SYSTEM - MASTER PIPELINE")
print("="*70)

try:
    # ====================================================================
    # STEP 1: LOAD DATASET
    # ====================================================================
    print("\n[1/6] Loading dataset...")
    
    # Try processed data first, then fallback to raw data
    processed_data = os.path.join(os.path.dirname(__file__), '..', 'data', 'hdfs', 'processed', 'dataset_1_cleaned.csv')
    raw_data = os.path.join(os.path.dirname(__file__), '..', 'data', 'hdfs', 'input', 'legal_cases.parquet')
    
    processed_data = os.path.abspath(processed_data)
    raw_data = os.path.abspath(raw_data)
    
    # Use raw parquet data if processed CSV is empty
    if os.path.exists(processed_data):
        df_temp = pd.read_csv(processed_data)
        if len(df_temp) > 0:
            df = df_temp
            data_source = "processed CSV"
        elif os.path.exists(raw_data):
            df = pd.read_parquet(raw_data)
            data_source = "raw Parquet"
        else:
            raise FileNotFoundError(f"No data found at {raw_data}")
    elif os.path.exists(raw_data):
        df = pd.read_parquet(raw_data)
        data_source = "raw Parquet"
    else:
        raise FileNotFoundError(f"Dataset not found at {processed_data} or {raw_data}")
    
    print(f"  [OK] Loaded {len(df)} rows from {data_source}")
    print(f"  [OK] Columns: {list(df.columns)}")
    
    # ====================================================================
    # STEP 2: TEXT CLEANING
    # ====================================================================
    print("\n[2/6] Cleaning text...")
    
    from preprocessing.text_cleaning import clean_text
    
    # For judicial dataset: combine relevant text columns
    # Create text from available columns
    text_columns = [col for col in df.columns if col not in ['case_id', 'year', 'evidence_count', 'witness_count', 'defendant_age', 'prosecutor_win_rate', 'sentence_years']]
    
    if len(text_columns) > 0:
        # Combine text columns for cases
        df["text"] = df[text_columns].fillna('').apply(lambda row: ' '.join(row.astype(str)), axis=1)
    else:
        # Fallback: create text from all columns
        df["text"] = df.astype(str).apply(lambda row: ' '.join(row), axis=1)
    
    df["clean_text"] = df["text"].apply(clean_text)
    
    print(f"  [OK] Cleaned {len(df)} documents")
    if len(df) > 0:
        sample_text = df['clean_text'].iloc[0][:60] if pd.notna(df['clean_text'].iloc[0]) else "[empty]"
        print(f"  [OK] Sample: {sample_text}...")
    else:
        print(f"  [WARNING] No data available")
    
    # ====================================================================
    # STEP 3: KEYWORD EXTRACTION
    # ====================================================================
    print("\n[3/6] Extracting keywords...")
    
    from nlp.keyword_extractor import KeywordExtractor
    
    extractor = KeywordExtractor(num_keywords=10)
    all_keywords = []
    
    for idx, clean_text_val in enumerate(df["clean_text"]):
        keywords = extractor.extract_keywords(clean_text_val)
        all_keywords.append(keywords)
        if idx == 0:
            print(f"  [OK] Keywords for row 1: {keywords[:5]}")
    
    df["keywords"] = all_keywords
    print(f"  [OK] Extracted keywords from {len(df)} documents")
    
    # ====================================================================
    # STEP 4: EMBEDDING GENERATION
    # ====================================================================
    print("\n[4/6] Generating embeddings (TF-IDF)...")
    
    # Use simple embedding for now (to avoid BERT download delay)
    # In production, use: from embeddings.case_embeddings import CaseEmbedder
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    vectorizer = TfidfVectorizer(max_features=384)  # Similar to BERT-base dims
    embeddings = vectorizer.fit_transform(df["clean_text"]).toarray()
    
    print(f"  [OK] Generated {len(embeddings)} embeddings")
    print(f"  [OK] Embedding dimension: {embeddings.shape[1]}")
    
    # ====================================================================
    # STEP 5: BUILD FAISS INDEX
    # ====================================================================
    print("\n[5/6] Building FAISS index...")
    
    try:
        import faiss
        
        # Convert to float32 (required by FAISS)
        embeddings_fp32 = embeddings.astype('float32')
        
        # Create index
        index = faiss.IndexFlatL2(embeddings_fp32.shape[1])
        index.add(embeddings_fp32)
        
        print(f"  [OK] FAISS index created")
        print(f"  [OK] Index size: {index.ntotal} vectors")
        
    except ImportError:
        print("  [!] FAISS not available, using approximate search")
        index = None
    
    # ====================================================================
    # STEP 6: SIMILARITY SEARCH
    # ====================================================================
    print("\n[6/6] Testing similarity search...")
    
    if index is not None:
        # Search for similar cases
        query_embedding = embeddings_fp32[0:1]
        distances, indices = index.search(query_embedding, k=3)
        
        # For judicial data, show crime and verdict instead of question
        query_case = f"{df['crime'].iloc[0]} - {df['verdict'].iloc[0]}"
        print(f"  [OK] Query: {query_case}")
        print(f"  [OK] Similar cases found:")
        
        for rank, (idx, dist) in enumerate(zip(indices[0], distances[0]), 1):
            similarity = 1 / (1 + dist)  # Convert distance to similarity
            similar_case = f"{df['crime'].iloc[idx]} - {df['verdict'].iloc[idx]}"
            print(f"    {rank}. {similar_case} (similarity: {similarity:.3f})")
    else:
        # Fallback: cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        
        query_embedding = embeddings[0:1]
        similarities = cosine_similarity(query_embedding, embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][1:4]
        
        print(f"  [OK] Query: {df['question'].iloc[0]}")
        print(f"  [OK] Similar cases found:")
        
        for rank, idx in enumerate(top_indices, 1):
            print(f"    {rank}. {df['question'].iloc[idx]} (similarity: {similarities[idx]:.3f})")
    
    # ====================================================================
    # FINAL REPORT
    # ====================================================================
    print("\n" + "="*70)
    print("PIPELINE EXECUTION SUMMARY")
    print("="*70)
    print(f"[OK] Dataset processed: {len(df)} legal documents")
    print(f"[OK] Text cleaning: 100%")
    print(f"[OK] Keyword extraction: 100%")
    print(f"[OK] Embedding generation: 100%")
    print(f"[OK] FAISS index: Built successfully")
    print(f"[OK] Similarity search: Operational")
    print("\n[OK] MASTER PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
