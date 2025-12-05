from fastapi import FastAPI
from api.ask import router as ask_router
from rag.qa import build_knowledge_base_from_dir

app = FastAPI()
app.include_router(ask_router)


@app.on_event("startup")
def startup_event():
    # Build knowledge base from COMP2123 notes
    notes_dir = "data/notes/COMP2123"
    try:
        build_knowledge_base_from_dir(notes_dir)
        print(f"Knowledge base built from: {notes_dir}")
    except Exception as e:
        # Do not crash the server if something goes wrong, just log it.
        print(f"Failed to build knowledge base: {e}")


@app.get("/health")
def health():
    return {"status": "ok"}
