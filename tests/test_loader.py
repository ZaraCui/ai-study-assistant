import os
from rag.loader import load_texts


def test_load_texts_reads_txt_files(tmp_path, monkeypatch):
    # prepare a temp notes dir with a txt file
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    file_path = notes_dir / "a.txt"
    content = "Hello world\nThis is a test file."
    file_path.write_text(content, encoding="utf-8")

    texts = load_texts(str(notes_dir))
    assert isinstance(texts, list)
    assert len(texts) == 1
    assert content in texts[0]
