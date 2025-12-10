"""Conftest for tests.

Kept intentionally minimal. Package install (e.g. `pip install -e .`)
is the recommended way to make `rag` importable in test/CI environments.
"""

def pytest_sessionstart(session):
    # no-op: keep conftest present for pytest hooks if needed in future
    return
