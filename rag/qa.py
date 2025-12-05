import os
import openai

from rag.embedder import model, embed_texts
from rag.vectorstore import VectorStore
from rag.prompt import build_prompt
from rag.loader import load_texts
from rag.chunker import chunk_text

# TODO: do NOT hard-code key in real projects.
# Read from environment variable instead.
openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")

# Global in-memory vector store
store = None  # will be initialized after building knowledge base


def build_knowledge_base_from_dir(folder_path: str):
    """
    Build the vector store from all notes under folder_path.
    This will:
      1) load raw texts (PDF/txt/md)
      2) chunk them
      3) embed all chunks
      4) populate the global vector store
    """
    global store

    raw_texts = load_texts(folder_path)
    all_chunks = []

    for text in raw_texts:
        # use your existing chunk_text function
        chunks = chunk_text(text)
        all_chunks.extend(chunks)

    if not all_chunks:
        raise ValueError("No chunks found. Did you put any notes in the folder?")

    vectors = embed_texts(all_chunks)
    dim = len(vectors[0])

    vs = VectorStore(dim)
    vs.add(vectors, all_chunks)
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
        # You forgot to call build_knowledge_base_from_dir somewhere (e.g. startup)
        return "Knowledge base is not initialized."

    q_vec = model.encode([question])[0]
    context_chunks = store.search(q_vec, top_k=3)
    prompt = build_prompt(question, context_chunks)

    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content
