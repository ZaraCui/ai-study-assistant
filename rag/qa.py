import os
import logging
import openai

from rag.embedder import model, embed_texts
from rag.vectorstore import VectorStore
from rag.prompt import build_prompt
from rag.loader import load_texts
from rag.chunker import chunk_text
from rag.token_manager import truncate_chunks_by_tokens, is_prompt_safe, estimate_tokens
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
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Read OpenAI key from environment (no hardcoding)
openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")

# For backward compatibility, maintain a global store reference to default course
store = None  # will be initialized after building knowledge base

# Default path prefix (for backward compatibility with old startup code)
DEFAULT_INDEX_PATH = os.getenv("INDEX_PATH", None)


def build_knowledge_base_from_dir(folder_path: str, index_path: str = None, course_code: str = None):
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
    
    # Try to load existing persisted index first
    try:
        logger.info(f"Attempting to load persisted index...")
        vs = VectorStore.load(index_path)
        set_course_store(course_code, vs)
        # For backward compatibility, also set global store to default course
        if course_code_upper == DEFAULT_COURSE:
            store = vs
        logger.info(f"Successfully loaded persisted index with {len(vs.texts)} chunks.")
        return vs
    except FileNotFoundError:
        logger.info(f"No persisted index found. Building from scratch...")
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

    # Cache the store
    set_course_store(course_code, vs)
    # For backward compatibility, also set global store
    if course_code_upper == DEFAULT_COURSE:
        store = vs
    
    logger.info("Knowledge base initialization complete.")
    return vs


def answer_question(question: str, course_code: str = None) -> str:
    """
    Run RAG-style QA for a specific course:
      1) select or load the course's knowledge base
      2) embed question
      3) search similar chunks
      4) truncate chunks if necessary to fit token limit
      5) build prompt
      6) check token safety
      7) ask OpenAI
      
    Args:
        question: The user's question.
        course_code: Which course to query. If None, uses DEFAULT_COURSE.
    
    Returns:
        Answer string or error message.
    """
    # Default to DEFAULT_COURSE if not specified
    if course_code is None:
        course_code = DEFAULT_COURSE
    
    course_code_upper = course_code.upper()
    logger.info(f"Answering question for course: {course_code_upper}")
    logger.debug(f"Question: {question}")
    
    # Try to get the store from cache, or load it
    course_store = get_course_store(course_code_upper)
    
    if course_store is None:
        logger.info(f"Course {course_code_upper} not in memory. Attempting to load...")
        course_store = load_course_store(course_code_upper)
    
    if course_store is None:
        error_msg = f"Knowledge base for course {course_code_upper} is not initialized."
        logger.error(error_msg)
        return f"Error: {error_msg} Please run: scripts/manage_index.py build --notes {get_course_notes_path(course_code)}"

    try:
        logger.debug(f"Encoding question...")
        q_vec = model.encode([question])[0]
        
        logger.debug("Searching for similar chunks...")
        context_chunks = course_store.search(q_vec, top_k=3)
        logger.info(f"Found {len(context_chunks)} relevant chunks.")
        
        # Token safety: truncate chunks if they would exceed token limit
        model_name = "gpt-4o-mini"
        max_context_tokens = 120000  # Conservative limit (gpt-4o-mini has 128k)
        safe_chunks = truncate_chunks_by_tokens(context_chunks, max_context_tokens)
        
        if len(safe_chunks) < len(context_chunks):
            logger.warning(
                f"Truncated context from {len(context_chunks)} chunks to {len(safe_chunks)} "
                f"to fit within token limit."
            )
        
        logger.debug("Building prompt...")
        prompt = build_prompt(question, safe_chunks)
        
        # Check if prompt is safe before sending to API
        is_safe, token_info = is_prompt_safe(prompt, model_name)
        logger.info(
            f"Prompt token estimate: {token_info['estimated_tokens']} / "
            f"{token_info['available_tokens']} available tokens"
        )
        
        if not is_safe:
            logger.warning(
                f"Prompt may exceed token limit. Attempting to truncate further..."
            )
            safe_chunks = truncate_chunks_by_tokens(safe_chunks, 15000)
            prompt = build_prompt(question, safe_chunks)
        
        logger.info(f"Calling OpenAI API for course {course_code_upper}...")
        resp = openai.chat.completions.create(
            model=model_name,
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
