"""
Course management for multi-course support.
Handles loading and switching between different course knowledge bases.
"""

import os
import logging
from typing import Optional, Dict, List

from rag.vectorstore import VectorStore

logger = logging.getLogger(__name__)

# In-memory cache of loaded course indexes
_course_stores: Dict[str, VectorStore] = {}

# Default course
DEFAULT_COURSE = os.getenv("DEFAULT_COURSE", "COMP2123")

# Base paths
NOTES_BASE_DIR = os.getenv("NOTES_BASE_DIR", "data/notes")
INDEX_BASE_DIR = os.getenv("INDEX_BASE_DIR", "data/index")


def get_course_notes_path(course_code: str) -> str:
    """
    Get the notes directory path for a course.

    Args:
        course_code: Course code (e.g., "COMP2123", "CS101").

    Returns:
        Full path to course notes directory.
    """
    return os.path.join(NOTES_BASE_DIR, course_code)


def get_course_index_path(course_code: str) -> str:
    """
    Get the index path prefix for a course.

    Args:
        course_code: Course code (e.g., "COMP2123", "CS101").

    Returns:
        Full path prefix for course index files.
    """
    # Create index directory if it doesn't exist
    os.makedirs(INDEX_BASE_DIR, exist_ok=True)
    return os.path.join(INDEX_BASE_DIR, course_code.lower())


def list_available_courses() -> List[str]:
    """
    List all available courses (folders in NOTES_BASE_DIR).

    Returns:
        List of course codes.
    """
    if not os.path.exists(NOTES_BASE_DIR):
        logger.warning(f"Notes directory not found: {NOTES_BASE_DIR}")
        return []

    courses = [
        d
        for d in os.listdir(NOTES_BASE_DIR)
        if os.path.isdir(os.path.join(NOTES_BASE_DIR, d))
    ]
    logger.info(f"Found {len(courses)} courses: {courses}")
    return sorted(courses)


def is_course_indexed(course_code: str) -> bool:
    """
    Check if a course has a persisted index.

    Args:
        course_code: Course code.

    Returns:
        True if index files exist, False otherwise.
    """
    index_path = get_course_index_path(course_code)
    index_file = f"{index_path}.index"
    texts_file = f"{index_path}_texts.pkl"

    exists = os.path.exists(index_file) and os.path.exists(texts_file)
    logger.debug(f"Course {course_code} indexed: {exists}")
    return exists


def get_course_store(course_code: str) -> Optional[VectorStore]:
    """
    Get the loaded VectorStore for a course.
    Returns None if not loaded.

    Args:
        course_code: Course code.

    Returns:
        VectorStore if loaded, None otherwise.
    """
    return _course_stores.get(course_code.upper())


def set_course_store(course_code: str, store: VectorStore) -> None:
    """
    Set the VectorStore for a course in cache.

    Args:
        course_code: Course code.
        store: VectorStore instance.
    """
    _course_stores[course_code.upper()] = store
    logger.info(f"Cached course store for {course_code.upper()}")


def load_course_store(course_code: str) -> Optional[VectorStore]:
    """
    Load a course's VectorStore from disk.
    If already cached, return cached version.

    Args:
        course_code: Course code.

    Returns:
        VectorStore if successfully loaded, None otherwise.
    """
    course_code_upper = course_code.upper()

    # Check if already cached
    if course_code_upper in _course_stores:
        logger.info(f"Using cached store for {course_code_upper}")
        return _course_stores[course_code_upper]

    # Try to load from disk
    index_path = get_course_index_path(course_code)
    logger.info(f"Attempting to load course {course_code_upper} from {index_path}")

    try:
        vs = VectorStore.load(index_path)
        _course_stores[course_code_upper] = vs
        n_chunks = len(vs.texts)
        msg = f"Successfully loaded course {course_code_upper} with {n_chunks} chunks"
        logger.info(msg)
        return vs
    except FileNotFoundError:
        logger.warning(f"No index found for course {course_code_upper}")
        return None
    except Exception as e:
        logger.error(f"Error loading course {course_code_upper}: {e}")
        return None


def get_course_info(course_code: str) -> Dict:
    """
    Get information about a course (indexed, chunk count, etc).

    Args:
        course_code: Course code.

    Returns:
        Dictionary with course info.
    """
    course_upper = course_code.upper()
    store = get_course_store(course_upper)
    notes_path = get_course_notes_path(course_code)
    indexed = is_course_indexed(course_code)

    info = {
        "course_code": course_upper,
        "indexed": indexed,
        "loaded": store is not None,
        "chunk_count": len(store.texts) if store else None,
        "notes_path": notes_path,
        "notes_exist": os.path.exists(notes_path),
    }

    return info


def clear_course_cache(course_code: Optional[str] = None) -> None:
    """
    Clear cached course stores.

    Args:
        course_code: Specific course to clear, or None to clear all.
    """
    if course_code:
        course_upper = course_code.upper()
        if course_upper in _course_stores:
            del _course_stores[course_upper]
            logger.info(f"Cleared cache for course {course_upper}")
    else:
        _course_stores.clear()
        logger.info("Cleared all course caches")


def list_loaded_courses() -> List[str]:
    """
    List all currently loaded courses.

    Returns:
        List of loaded course codes.
    """
    return sorted(list(_course_stores.keys()))
