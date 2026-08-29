import os
import re
import numpy as np
from typing import List

class VectorEmbedder:
    _model = None
    _tried_loading_model = False

    @classmethod
    def get_model(cls):
        if not cls._tried_loading_model:
            cls._tried_loading_model = True
            try:
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer("all-MiniLM-L6-v2")
                print("[VectorEmbedder] Successfully loaded SentenceTransformer model ('all-MiniLM-L6-v2').")
            except Exception as e:
                print(f"[VectorEmbedder] SentenceTransformer not loaded ({e}). Using feature-hashing dense vectorizer.")
                cls._model = False
        return cls._model

    @classmethod
    def embed_texts(cls, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of text strings."""
        if not texts:
            return []

        model = cls.get_model()
        if model:
            try:
                embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                return embeddings.tolist()
            except Exception as e:
                print(f"[VectorEmbedder] SentenceTransformer error: {e}")

        # Clean, high-precision Word & Bigram Feature Hashing Vectorizer (384 dimensions)
        return [cls._hash_vectorize(t) for t in texts]

    @classmethod
    def embed_query(cls, query: str) -> List[float]:
        """Generates embedding vector for a single query string."""
        res = cls.embed_texts([query])
        return res[0] if res else [0.0] * 384

    @staticmethod
    def _hash_vectorize(text: str, dim: int = 384) -> List[float]:
        """
        Creates a clean dense vector representation using word tokens and word bigrams.
        Guarantees that document chunks and queries share the exact same feature space.
        """
        vec = np.zeros(dim, dtype=float)
        if not text:
            return vec.tolist()

        # Extract lower-case words (length >= 2)
        words = [w for w in re.findall(r'\b[a-zA-Z0-9]{2,}\b', text.lower())]
        
        # Word unigrams
        for word in words:
            idx = abs(hash(word)) % dim
            vec[idx] += 1.0

        # Word bigrams (for context combinations like "cse fee", "hostel fee")
        for i in range(len(words) - 1):
            bigram = f"{words[i]}_{words[i+1]}"
            idx = abs(hash(bigram)) % dim
            vec[idx] += 1.5

        # Normalize vector to unit L2 length
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
