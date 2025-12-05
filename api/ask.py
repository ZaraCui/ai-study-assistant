from fastapi import APIRouter, Query
from typing import Optional
from rag.qa import answer_question
from rag.course_manager import list_available_courses, get_course_info, list_loaded_courses, DEFAULT_COURSE

router = APIRouter()

@router.get("/ask")
def ask(q: str, course: Optional[str] = Query(None, description=f"Course code (default: {DEFAULT_COURSE})")):
    """
    Ask a question about course materials.
    
    Query parameters:
      - q: The question (required)
      - course: Course code like 'COMP2123' or 'CS101' (optional, defaults to DEFAULT_COURSE)
    
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

