import shutil
import os
from src.utils import ensure_dirs

def cleanup_vectordb():
    """Step 10: Delete and recreate vector database"""
    db_path = "data/chroma_db"
    if os.path.exists(db_path):
        print(f"Removing old vector DB at {db_path}")
        shutil.rmtree(db_path)
        print("Vector DB cleared successfully")
    else:
        print("Vector DB path not found")

    ensure_dirs()

if __name__ == "__main__":
    cleanup_vectordb()
