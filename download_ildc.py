import sys
try:
    from datasets import load_dataset
    import pandas as pd
except ImportError:
    print("Please install datasets and pandas")
    sys.exit(1)

print("Downloading real Indian Legal Documents Corpus (ILDC) from HuggingFace...")
try:
    # Joelito's ILDC is a standard mirror without authentication gates for the base dataset
    dataset = load_dataset("joelito/ildc-multi")
    df = dataset['train'].to_pandas()
    
    # Take first 2000 real cases
    df_small = df.head(2000)
    
    # Save the text and label columns mapping what we need
    if 'text' in df_small.columns:
        # Just save text and label
        out_df = pd.DataFrame()
        out_df['text'] = df_small['text']
        out_df['label'] = df_small['label'] if 'label' in df_small.columns else 0
        out_df.to_csv("data/raw/ildc.csv", index=False)
        print("Success! Downloaded 2000 real Indian cases to data/raw/ildc.csv")
    else:
        print("Columns found:", df_small.columns)
except Exception as e:
    print("Failed to download using joelito/ildc-multi:", e)
    print("Trying fallback to another public repo...")
    try:
        dataset = load_dataset("Exploration-Lab/ILDC")
        df = dataset['train'].to_pandas()
        df_small = df.head(2000)
        out_df = pd.DataFrame()
        out_df['text'] = df_small['text']
        out_df['label'] = df_small['label'] if 'label' in df_small.columns else 0
        out_df.to_csv("data/raw/ildc.csv", index=False)
        print("Success! Downloaded 2000 real Indian cases to data/raw/ildc.csv")
    except Exception as e2:
        print("Failed both attempts. Please ensure internet access to Huggingface.", e2)
