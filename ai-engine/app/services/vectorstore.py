from typing import List, Tuple

class InMemoryVectorStore:
    """A tiny in-memory vector store for development and tests.

    Stores tuples of (id, text, vector) and supports simple cosine-like scoring
    via dot product on the pseudo-embeddings returned by `EmbeddingService`.
    """

    def __init__(self):
        self._items: List[Tuple[str, str, List[float]]] = []

    def add_documents(self, docs: List[Tuple[str, str, List[float]]]):
        """Add documents where each item is (id, text, vector)."""
        for doc in docs:
            self._items.append(doc)

    def search(self, query_vector: List[float], top_k: int = 5):
        """Return top_k documents by simple dot-product score."""
        scores = []
        for doc_id, text, vec in self._items:
            # compute dot-product
            s = sum(a * b for a, b in zip(query_vector, vec))
            scores.append((s, doc_id, text))
        scores.sort(reverse=True, key=lambda x: x[0])
        return [{"id": doc_id, "text": text, "score": float(score)} for score, doc_id, text in scores[:top_k]]

    def clear(self):
        self._items.clear()
