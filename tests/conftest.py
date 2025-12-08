import sys
import os

# Ensure project root is on sys.path so tests can import top-level packages
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def pytest_sessionstart(session):
    print('\n[conftest] CWD:', os.getcwd())
    print('[conftest] inserted project_root:', project_root)
    print('[conftest] sys.path[0]:', sys.path[0])
    print('[conftest] sys.path sample:', sys.path[:5])
    try:
        import importlib
        spec = importlib.util.find_spec('rag')
        print('[conftest] find_spec("rag") ->', spec)
    except Exception as e:
        print('[conftest] import check error:', e)
