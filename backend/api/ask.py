import os
import sys
from fastapi import APIRouter, Query # type: ignore
from typing import Optional

# Define the default course here
DEFAULT_COURSE = os.getenv("DEFAULT_COURSE", "COMP2123")  # default: "COMP2123"

# Ensure we can import backend modules
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(backend_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.rag.qa import answer_question, build_knowledge_base_from_dir
from backend.rag.course_manager import (
    list_available_courses,
    get_course_info,
    list_loaded_courses,
    get_course_notes_path,
    get_course_index_path,
)

router = APIRouter()

# Ask endpoint
@router.get("/ask")
def ask(
    q: str,
    course: Optional[str] = Query(
        None, description=f"Course code (default: {DEFAULT_COURSE})"
    ),
):
    """Ask a question about course materials."""
    return {"answer": answer_question(q, course)}

# List all available courses
@router.get("/courses")
def list_courses():
    """List all available courses."""
    available = list_available_courses()
    loaded = list_loaded_courses()
    return {
        "default_course": DEFAULT_COURSE,
        "available_courses": available,
        "loaded_courses": loaded,
    }

# Get information about a specific course
@router.get("/courses/{course_code}")
def course_info(course_code: str):
    """Get information about a specific course."""
    info = get_course_info(course_code)
    return info

# Rebuild the index for a specific course
@router.post("/courses/{course_code}/reload")
def reload_course(course_code: str):
    """Rebuild the index for a specific course."""
    notes = get_course_notes_path(course_code)
    index_path = get_course_index_path(course_code)

    try:
        build_knowledge_base_from_dir(notes, index_path, course_code)
        return {"status": "ok", "course": course_code, "index_path": index_path}
    except Exception as e:
        return {"status": "error", "error": str(e)}
