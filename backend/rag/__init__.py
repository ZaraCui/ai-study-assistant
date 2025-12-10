"""rag package initializer.

This file makes the `rag` directory an importable package for tests
and tools that expect a regular package (avoids ModuleNotFoundError).
"""

__all__ = [
    "chunker",
    "course_manager",
    "embedder",
    "loader",
    "prompt",
    "qa",
    "token_manager",
    "vectorstore",
]
