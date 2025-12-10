import os
import logging
import openai

from rag.embedder import embed_texts
from rag.vectorstore import VectorStore
from rag.prompt import build_prompt
from rag.loader import load_texts
from rag.chunker import chunk_text
from rag.token_manager import truncate_chunks_by_tokens, is_prompt_safe
from rag.course_manager import (
    get_course_store,
    set_course_store,
    load_course_store,
    get_course_notes_path,
    get_course_index_path,
    DEFAULT_COURSE,
)

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Read OpenAI key from environment (no hardcoding)
openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")

# For backward compatibility, maintain a global store reference to default course
store = None  # will be initialized after building knowledge base

# Default path prefix (for backward compatibility with old startup code)
DEFAULT_INDEX_PATH = os.getenv("INDEX_PATH", None)

# Ensure absolute path to avoid issues on Render
def ensure_abs(path_prefix: str) -> str:
    """
    Converts relative paths to absolute paths for Render compatibility
    """
    return os.path.abspath(path_prefix)


def build_knowledge_base_from_dir(
    folder_path: str, index_path: str = None, course_code: str = None
):
    """
    Build or load the vector store from notes under folder_path.

    For backward compatibility:
      - If course_code is None, defaults to DEFAULT_COURSE
      - If index_path is provided, uses that instead of default course path

    Behavior:
      - If a persisted index exists at `index_path`, load it and cache it.
      - Otherwise, load raw texts, chunk, embed, build an in-memory VectorStore,
        save it to `index_path`, and cache it.
    """
    global store

    # Determine course code
    if course_code is None:
        course_code = DEFAULT_COURSE

    course_code_upper = course_code.upper()

    # Determine index path
    if index_path is None:
        index_path = get_course_index_path(course_code)

    logger.info(f"Initializing knowledge base for course {course_code_upper}")
    logger.info(f"Notes directory: {folder_path}")
    logger.info(f"Index path: {index_path}")

    # Ensure absolute path for the index
    index_path = ensure_abs(index_path)

    # Try to load existing persisted index first
    try:
        logger.info("Attempting to load persisted index...")
        vs = VectorStore.load(index_path)
        set_course_store(course_code, vs)
        # For backward compatibility, also set global store to default course
        if course_code_upper == DEFAULT_COURSE:
            store = vs
        logger.info(f"Successfully loaded persisted index with {len(vs.texts)} chunks.")
        return vs
    except FileNotFoundError:
        logger.info("No persisted index found. Building from scratch...")
    except Exception as e:
        logger.warning(f"Error loading persisted index: {e}. Building from scratch...")

    # Build from scratch
    try:
        logger.info(f"Loading text files from: {folder_path}")
        raw_texts = load_texts(folder_path)
        logger.info(f"Loaded {len(raw_texts)} text files.")
    except Exception as e:
        logger.error(f"Failed to load texts from {folder_path}: {e}")
        raise

    all_chunks = []
    try:
        logger.info("Chunking texts...")
        for i, text in enumerate(raw_texts):
            chunks = chunk_text(text)
            all_chunks.extend(chunks)
            logger.debug(f"File {i+1}/{len(raw_texts)}: {len(chunks)} chunks")
        logger.info(f"Total chunks created: {len(all_chunks)}")
    except Exception as e:
        logger.error(f"Error during chunking: {e}")
        raise

    if not all_chunks:
        error_msg = "No chunks found. Did you put any notes in the folder?"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        logger.info("Embedding chunks...")
        vectors = embed_texts(all_chunks)
        dim = len(vectors[0])
        logger.info(f"Embeddings created: {len(vectors)} vectors of dimension {dim}")
    except Exception as e:
        logger.error(f"Error during embedding: {e}")
        raise

    try:
        logger.info("Building FAISS index...")
        vs = VectorStore(dim)
        vs.add(vectors, all_chunks)
        logger.info("FAISS index built successfully.")
    except Exception as e:
        logger.error(f"Error building FAISS index: {e}")
        raise

    # Save the built index for future runs
    try:
        logger.info(f"Saving index to: {index_path}")
        vs.save(index_path)
        logger.info("Index saved successfully.")
    except Exception as e:
        error_detail = f"Failed to save vector index to {index_path}: {e}"
        logger.warning(f"{error_detail}. Continuing without persistence.")

    # Cache the store
    set_course_store(course_code, vs)
    # For backward compatibility, also set global store
    if course_code_upper == DEFAULT_COURSE:
        store = vs

    logger.info("Knowledge base initialization complete.")
    return vs
