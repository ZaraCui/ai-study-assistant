import os
import logging
from fastapi import FastAPI

from backend.api.ask import router as ask_router
from backend.rag.qa import build_knowledge_base_from_dir

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()
app.include_router(ask_router)


@app.on_event("startup")
def startup_event():
    # Load configuration from environment variables
    notes_dir = os.getenv("NOTES_DIR", "data/notes/COMP2123")
    index_path = os.getenv("INDEX_PATH", "data/index/comp2123")

    logger.info("=== AI Study Assistant Startup ===")
    logger.info(f"Notes directory: {notes_dir}")
    logger.info(f"Index path: {index_path}")

    try:
        build_knowledge_base_from_dir(notes_dir, index_path)
        logger.info("✓ Knowledge base initialized successfully.")
    except Exception as e:
        logger.error(f"✗ Failed to build knowledge base: {e}", exc_info=True)
        logger.warning(
            "Server will continue running but /ask endpoint will not be functional."
        )


@app.get("/health")
def health():
    return {"status": "ok"}
