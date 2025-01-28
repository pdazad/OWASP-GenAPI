import os

MODEL_PATH = os.getenv("MODEL_PATH", "pdazad/fine_tuned_bloom_owasp")
INDEX_PATH = os.getenv("INDEX_PATH", "./data/model/indice_faiss.index")
PROCESSED_DATA_PATH = os.getenv("PROCESSED_DATA_PATH", "./data/model/owasp_cleaned_dataset.json")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L12-v2")
TOP_K = int(os.getenv("TOP_K", 3))
