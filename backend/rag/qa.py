import os
import logging
from functools import lru_cache

from .vectorstore import VectorStore
from .loader import load_texts

logger = logging.getLogger(__name__)


# -------------------------------------------------------
# Load persisted FAISS + text chunks
# -------------------------------------------------------
def load_persisted_vectorstore(index_dir: str) -> VectorStore:
    vs = VectorStore(index_dir)
    vs.load()  # load FAISS + pkl
    logger.info(f"[VectorStore] Loaded {len(vs.text_chunks)} text chunks.")
    return vs


# -------------------------------------------------------
# Cached global accessor
# -------------------------------------------------------
@lru_cache(maxsize=1)
def get_vectorstore(notes_path: str, index_path: str) -> VectorStore:

    logger.info("Initializing knowledge base for COMP2123")
    logger.info(f"Notes dir: {notes_path}")
    logger.info(f"Index path: {index_path}")

    index_file = index_path + ".index"
    text_file = index_path + "_texts.pkl"

    if not (os.path.exists(index_file) and os.path.exists(text_file)):
        raise RuntimeError(
            f"❌ Precomputed index missing at {index_path}. "
            f"Run scripts/build_index.py locally and commit the files."
        )

    return load_persisted_vectorstore(index_path)


# -------------------------------------------------------
# ONLY search, NO embedding, NO LLM
# -------------------------------------------------------
def answer_question(question: str, course: str = None):
    notes_dir = os.getenv("NOTES_DIR", "backend/data/notes/C
