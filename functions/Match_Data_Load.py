# functions/Match_Data_Load.py

import pandas as pd
import os

MATCH_DATA_DIR = "data/Match Data"
CACHE_FILE = "data/match_data_cache.parquet"


def load_preprocessed_match_data(force_rebuild=False):
    """
    Load and combine all match-level data from the designated folder. 
    Files are assumed to be pre-cleaned and have consistent structure.
    """
    if os.path.exists(CACHE_FILE) and not force_rebuild:
        return pd.read_parquet(CACHE_FILE)

    all_dfs = []

    for file in os.listdir(MATCH_DATA_DIR):
        if file.endswith(".csv"):
            try:
                df = pd.read_csv(os.path.join(MATCH_DATA_DIR, file))
                df["source_file"] = file
                all_dfs.append(df)
            except Exception as e:
                print(f"⚠️ Failed to load {file}: {e}")

    if not all_dfs:
        return pd.DataFrame()

    combined = pd.concat(all_dfs, ignore_index=True)

    # Ensure all columns are string unless explicitly numeric
    combined.columns = [str(col) for col in combined.columns]
    for col in combined.columns:
        try:
            combined[col] = pd.to_numeric(combined[col], errors="ignore")
        except:
            pass
        if not pd.api.types.is_numeric_dtype(combined[col]) and not pd.api.types.is_bool_dtype(combined[col]):
            combined[col] = combined[col].astype(str)

    try:
        combined.to_parquet(CACHE_FILE, index=False)
    except Exception as e:
        print(f"❌ Failed to write match data cache: {e}")

    return combined

