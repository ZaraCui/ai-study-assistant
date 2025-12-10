import os
import sys
import logging

# === Fix import path ===
# Add project root (the directory containing "backend") into sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.rag.qa import build_knowledge_base_from_dir

logging.basicConfig(level=logging.INFO)

NOTES_DIR = "backend/data/notes/COMP2123"
INDEX_DIR = "backend/data/index/comp2123"

if __name__ == "__main__":
    notes_path = os.path.abspath(NOTES_DIR)
    index_path = os.path.abspath(INDEX_DIR)

    print("Building index from:", notes_path)
    print("Saving index to:", index_path)

    build_knowledge_base_from_dir(notes_path, index_path)

    print("Index build complete!")
