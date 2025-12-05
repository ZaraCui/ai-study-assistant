import os
from fastapi import FastAPI
from api.ask import router as ask_router
from rag.qa import build_knowledge_base_from_dir

app = FastAPI()
app.include_router(ask_router)


@app.on_event("startup")
def startup_event():
    # Load configuration from environment variables
    notes_dir = os.getenv("NOTES_DIR", "data/notes/COMP2123")
    index_path = os.getenv("INDEX_PATH", "data/index/comp2123")
    
    try:
        build_knowledge_base_from_dir(notes_dir, index_path)
        print(f"Knowledge base built from: {notes_dir}")
        print(f"Index persisted at: {index_path}")
    except Exception as e:
        # Do not crash the server if something goes wrong, just log it.
        print(f"Failed to build knowledge base: {e}")


@app.get("/health")
def health():
    return {"status": "ok"}
