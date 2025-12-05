import os
import logging
import openai

from rag.embedder import model, embed_texts
from rag.vectorstore import VectorStore
from rag.prompt import build_prompt
from rag.loader import load_texts
from rag.chunker import chunk_text

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Read OpenAI key from environment (no hardcoding)
openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")

# Global in-memory vector store
store = None  # will be initialized after building knowledge base

# Default path prefix for persisted index/texts (can be overridden via INDEX_PATH env var)
DEFAULT_INDEX_PATH = os.getenv("INDEX_PATH", "data/index/comp2123")


def build_knowledge_base_from_dir(folder_path: str, index_path: str = DEFAULT_INDEX_PATH):
    """
    Build or load the vector store from notes under folder_path.

    Behavior:
      - If a persisted index exists at `index_path`, load it and set global `store`.
      - Otherwise, load raw texts, chunk, embed, build an in-memory VectorStore,
        save it to `index_path`, and set global `store`.
    """
    global store

    logger.info(f"Initializing knowledge base from: {folder_path}")

    # Try to load existing persisted index first
    try:
        logger.info(f"Attempting to load persisted index from: {index_path}")
        vs = VectorStore.load(index_path)
        store = vs
        logger.info(f"Successfully loaded persisted index with {len(vs.texts)} chunks.")
        return
    except FileNotFoundError:
        logger.info(f"No persisted index found at {index_path}. Building from scratch...")
    except Exception as e:
        logger.warning(f"Error loading persisted index: {e}. Building from scratch...")

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
        logger.info(f"FAISS index built successfully.")
    except Exception as e:
        logger.error(f"Error building FAISS index: {e}")
        raise

    # Save the built index for future runs
    try:
        logger.info(f"Saving index to: {index_path}")
        vs.save(index_path)
        logger.info(f"Index saved successfully.")
    except Exception as e:
        logger.warning(f"Failed to save vector index to {index_path}: {e}. Continuing without persistence.")

    store = vs
    logger.info("Knowledge base initialization complete.")


def answer_question(question: str) -> str:
    """
    Run RAG-style QA:
      1) embed question
      2) search similar chunks
      3) build prompt
      4) ask OpenAI
    """
    if store is None:
        logger.error("Knowledge base is not initialized. Cannot answer question.")
        return "Knowledge base is not initialized."

    try:
        logger.debug(f"Encoding question: {question}")
        q_vec = model.encode([question])[0]
        
        logger.debug("Searching for similar chunks...")
        context_chunks = store.search(q_vec, top_k=3)
        logger.info(f"Found {len(context_chunks)} relevant chunks.")
        
        logger.debug("Building prompt...")
        prompt = build_prompt(question, context_chunks)
        
        logger.info("Calling OpenAI API...")
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = resp.choices[0].message.content
        logger.info("Answer generated successfully.")
        return answer
    
    except openai.AuthenticationError as e:
        logger.error(f"OpenAI authentication failed. Check your OPENAI_API_KEY: {e}")
        return f"Error: Authentication failed. Please check your OpenAI API key."
    except openai.RateLimitError as e:
        logger.error(f"OpenAI rate limit exceeded: {e}")
        return f"Error: Too many requests to OpenAI. Please try again later."
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        return f"Error: OpenAI API error. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error in answer_question: {e}", exc_info=True)
        return f"Error: {str(e)}"
