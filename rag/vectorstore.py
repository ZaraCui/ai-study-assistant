import faiss
import numpy as np
import pickle
import os


class VectorStore:
    """Simple FAISS-backed vector store with optional persistence.

    Files created by `save(path)`:
      - <path>.index        (faiss index)
      - <path>_texts.pkl   (pickled list of texts)
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
        # protect against missing texts (shouldn't normally happen)
        return [self.texts[i] for i in indices[0] if i is not None and i < len(self.texts)]

    def save(self, path_prefix: str):
        """Save FAISS index and texts using the provided path prefix.

        Example: `vs.save('data/index/comp2123')` will write
                 `data/index/comp2123.index` and `data/index/comp2123_texts.pkl`
        """
        os.makedirs(os.path.dirname(path_prefix) or ".", exist_ok=True)
        index_file = f"{path_prefix}.index"
        texts_file = f"{path_prefix}_texts.pkl"
        faiss.write_index(self.index, index_file)
        with open(texts_file, "wb") as f:
            pickle.dump(self.texts, f)

    @classmethod
    def load(cls, path_prefix: str):
        """Load a saved FAISS index and texts from the given path prefix.

        Returns a VectorStore instance.
        """
        index_file = f"{path_prefix}.index"
        texts_file = f"{path_prefix}_texts.pkl"
        if not os.path.exists(index_file) or not os.path.exists(texts_file):
            raise FileNotFoundError(f"Index or texts file not found at: {path_prefix}")

        index = faiss.read_index(index_file)
        with open(texts_file, "rb") as f:
            texts = pickle.load(f)

        try:
            dim = index.d
        except Exception:
            dim = None

        return cls(dim=dim, index=index, texts=texts)
