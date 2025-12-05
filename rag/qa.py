import os
import openai

from rag.embedder import model, embed_texts
from rag.vectorstore import VectorStore
from rag.prompt import build_prompt
from rag.loader import load_texts
from rag.chunker import chunk_text

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

    # Try to load existing persisted index first
    try:
        vs = VectorStore.load(index_path)
        store = vs
        return
    except FileNotFoundError:
        # no persisted index found; continue to build
        pass

    raw_texts = load_texts(folder_path)
    all_chunks = []

    for text in raw_texts:
        chunks = chunk_text(text)
        all_chunks.extend(chunks)

    if not all_chunks:
        raise ValueError("No chunks found. Did you put any notes in the folder?")

    vectors = embed_texts(all_chunks)
    dim = len(vectors[0])

    vs = VectorStore(dim)
    vs.add(vectors, all_chunks)

    # Save the built index for future runs
    try:
        vs.save(index_path)
    except Exception as e:
        # do not fail the whole flow if saving fails; log instead
        print(f"Warning: failed to save vector index: {e}")

    store = vs


def answer_question(question: str) -> str:
    """
    Run RAG-style QA:
      1) embed question
      2) search similar chunks
      3) build prompt
      4) ask OpenAI
    """
    if store is None:
        return "Knowledge base is not initialized."

    q_vec = model.encode([question])[0]
    context_chunks = store.search(q_vec, top_k=3)
    prompt = build_prompt(question, context_chunks)

    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content
