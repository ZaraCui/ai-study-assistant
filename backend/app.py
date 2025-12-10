import os
import sys
import logging
from fastapi import FastAPI

# -------------------------------------------------------------------
# Fix Python path so "backend" module is importable on Render
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)                      # project root

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -------------------------------------------------------------------
# Now imports succeed consistently (both locally & on Render)
# -------------------------------------------------------------------
from backend.api.ask import router as ask_router
from backend.rag.qa import build_knowledge_base_from_dir


# -------------------------------------------------------------------
# Logging Configuration
# -------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# -------------------------------------------------------------------
# FastAPI App
# -------------------------------------------------------------------
app = FastAPI()
app.include_router(ask_router)


# -------------------------------------------------------------------
# Startup: Load Knowledge Base
# -------------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    """
    Load COMP2123 knowledge base at startup using:
    - Environment variables if provided
    - Otherwise stable absolute paths (backend/data/...)
    """

    # Absolute fallback paths (Render-safe)
    default_notes = os.path.join(BASE_DIR, "data/notes/COMP2123")
    default_index = os.path.join(BASE_DIR, "data/index/comp2123")

    notes_dir = os.getenv("NOTES_DIR", default_notes)
    index_path = os.getenv("INDEX_PATH", default_index)

    logger.info("=== AI Study Assistant Startup ===")
    logger.info(f"Notes directory: {notes_dir}")
    logger.info(f"Index path: {index_path}")

    try:
        build_knowledge_base_from_dir(notes_dir, index_path)
        logger.info("✓ Knowledge base initialized successfully.")
    except Exception as e:
        logger.error(f"✗ Failed to build knowledge base: {e}", exc_info=True)
        logger.warning(
            "Server will continue running but /ask endpoint will NOT be functional."
        )


# -------------------------------------------------------------------
# Health Check Endpoint
# -------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
