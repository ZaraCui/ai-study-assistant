import faiss
import numpy as np

class VectorStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, vectors, chunks):
        vectors = np.array(vectors).astype("float32")
        self.index.add(vectors)
        self.texts.extend(chunks)

    def search(self, query_vector, top_k=3):
        query_vector = np.array([query_vector]).astype("float32")
        _, indices = self.index.search(query_vector, top_k)
        return [self.texts[i] for i in indices[0]]
