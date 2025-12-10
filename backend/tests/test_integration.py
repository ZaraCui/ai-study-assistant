import os
from types import SimpleNamespace

from backend.rag.qa import build_knowledge_base_from_dir, answer_question
import backend.rag.embedder as embedder


def test_build_and_query_integration(tmp_path, monkeypatch):
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    (notes_dir / "n1.txt").write_text("This is a test note. " * 200, encoding="utf-8")

    index_path = str(tmp_path / "index" / "testcourse")
    os.makedirs(os.path.dirname(index_path), exist_ok=True)

    # Monkeypatch embedder model to avoid heavy downloads
    class DummyModel:
        def encode(self, texts):
            return [[0.1] * 8 for _ in texts]

    monkeypatch.setattr(embedder, "get_model", lambda: DummyModel())

    # Monkeypatch openai completion to avoid network calls
    import backend.rag.qa as qa_module

    def fake_create(*args, **kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="DUMMY ANSWER"))]
        )

    monkeypatch.setattr(qa_module.openai.chat.completions, "create", fake_create)

    # Build the knowledge base for this test course
    build_knowledge_base_from_dir(
        str(notes_dir), index_path=index_path, course_code="TESTCOURSE"
    )

    # Query the course
    ans = answer_question("what is testing?", course_code="TESTCOURSE")
    assert "DUMMY ANSWER" in ans
