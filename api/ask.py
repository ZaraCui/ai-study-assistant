from fastapi import APIRouter, Query
from typing import Optional
from rag.qa import answer_question
from rag.course_manager import (
    list_available_courses,
    get_course_info,
    list_loaded_courses,
    DEFAULT_COURSE,
)
from rag.course_manager import get_course_notes_path, get_course_index_path
from rag.qa import build_knowledge_base_from_dir

router = APIRouter()


@router.get("/ask")
def ask(
    q: str,
    course: Optional[str] = Query(
        None, description=f"Course code (default: {DEFAULT_COURSE})"
    ),
):
    """
    Ask a question about course materials.

    Query parameters:
      - q: The question (required)
      - course: Course code (e.g. 'COMP2123', 'CS101') (defaults to DEFAULT_COURSE)

    Example:
      GET /ask?q=what+is+polymorphism&course=COMP2123
    """
    return {"answer": answer_question(q, course)}


@router.get("/courses")
def list_courses():
    """
    List all available courses (folders in data/notes/).
    """
    available = list_available_courses()
    loaded = list_loaded_courses()
    return {
        "default_course": DEFAULT_COURSE,
        "available_courses": available,
        "loaded_courses": loaded,
    }


@router.get("/courses/{course_code}")
def course_info(course_code: str):
    """
    Get information about a specific course (indexed, chunk count, etc).
    """
    info = get_course_info(course_code)
    return info


@router.post("/courses/{course_code}/reload")
def reload_course(course_code: str):
    """
    Reload (rebuild and cache) the index for a specific course.
    """
    notes = get_course_notes_path(course_code)
    index_path = get_course_index_path(course_code)
    try:
        build_knowledge_base_from_dir(notes, index_path, course_code)
        return {"status": "ok", "course": course_code, "index_path": index_path}
    except Exception as e:
        return {"status": "error", "error": str(e)}
