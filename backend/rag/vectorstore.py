import faiss
import numpy as np
import pickle
import os


def ensure_abs(path_prefix: str) -> str:
    """
    Render 部署最关键的修复：
    自动把相对路径变成绝对路径，避免部署环境找不到文件。
    """
    return os.path.abspath(path_prefix)


class VectorStore:
    """
    Simple FAISS-backed vector store with optional persistence.

    Files created by save(path_prefix):
      - <path_prefix>.index
      - <path_prefix>_texts.pkl
    """

    def __init__(self, dim=None, index=None, texts=None):
        if index is not None:
            self.index = index
            try:
                dim = index.d
            except Exception:
                pass
        else:
            if dim is None:
                raise ValueError("Either 'dim' or 'index' must be provided")
            self.index = faiss.IndexFlatL2(dim)

        self.texts = texts or []

    def add(self, vectors, chunks):
        vectors = np.array(vectors).astype("float32")
        self.index.add(vectors)
        self.texts.extend(chunks)

    def search(self, query_vector, top_k=3):
        query_vector = np.array([query_vector]).astype("float32")
        _, indices = self.index.search(query_vector, top_k)
        return [
            self.texts[i] for i in indices[0]
            if i is not None and i < len(self.texts)
        ]

    def save(self, path_prefix: str):
        """
        Save FAISS index and texts using absolute path.
        Render 部署必须使用绝对路径。
        """
        path_prefix = ensure_abs(path_prefix)
        os.makedirs(os.path.dirname(path_prefix), exist_ok=True)

        index_file = f"{path_prefix}.index"
        texts_file = f"{path_prefix}_texts.pkl"

        faiss.write_index(self.index, index_file)
        with open(texts_file, "wb") as f:
            pickle.dump(self.texts, f)

        print(f"[VectorStore] Saved index to {index_file}")
        print(f"[VectorStore] Saved texts to {texts_file}")

    @classmethod
    def load(cls, path_prefix: str):
        """
        Load a saved FAISS index + texts using absolute path.
        """
        path_prefix = ensure_abs(path_prefix)

        index_file = f"{path_prefix}.index"
        texts_file = f"{path_prefix}_texts.pkl"

        print(f"[VectorStore] Attempting to load index at: {index_file}")
        print(f"[VectorStore] Attempting to load texts at: {texts_file}")

        if not os.path.exists(index_file) or not os.path.exists(texts_file):
            raise FileNotFoundError(f"Index or texts file not found at: {path_prefix}")

        index = faiss.read_index(index_file)

        with open(texts_file, "rb") as f:
            texts = pickle.load(f)

        try:
            dim = index.d
        except Exception:
            dim = None

        print(f"[VectorStore] Successfully loaded FAISS index (dim={dim})")
        print(f"[VectorStore] Loaded {len(texts)} text chunks")

        return cls(dim=dim, index=index, texts=texts)
