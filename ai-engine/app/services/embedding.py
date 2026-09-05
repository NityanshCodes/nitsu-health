from typing import List
import os


class EmbeddingService:
    """Placeholder embedding service.

    Returns simple fixed-length vectors based on input length so downstream
    components can be wired before a real vector model is added.
    """

    def __init__(self):
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors = []
        for t in texts:
            l = len(t)
            # deterministic pseudo-embedding: repeated normalized length
            vectors.append([float(l) / (i + 1) for i in range(8)])
        return vectors
