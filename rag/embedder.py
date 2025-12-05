from typing import Optional

_model = None


def get_model():
    """Lazily load the sentence-transformers model to avoid heavy downloads at import time."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_texts(texts):
    model = get_model()
    return model.encode(texts)
