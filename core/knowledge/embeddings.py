import hashlib
import math
import os
import re
import unicodedata
from typing import Dict, List, Optional, Tuple

from agno.knowledge.embedder.base import Embedder


class LocalHashEmbedder(Embedder):
    def __init__(self, dimensions: int = 1536):
        self.dimensions = dimensions

    def _tokens(self, text: str) -> List[str]:
        normalized = unicodedata.normalize("NFKD", text.lower())
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        return re.findall(r"[a-z0-9]+", ascii_text)

    def get_embedding(self, text: str) -> List[float]:
        if self.dimensions is None:
            raise ValueError("dimensions must be set")

        dim = self.dimensions
        vector = [0.0] * dim
        tokens = self._tokens(text)

        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(v * v for v in vector))
        return vector if norm == 0 else [v / norm for v in vector]

    def get_embedding_and_usage(self, text: str) -> Tuple[List[float], Optional[Dict]]:
        return self.get_embedding(text), None

    async def async_get_embedding(self, text: str) -> List[float]:
        return self.get_embedding(text)

    async def async_get_embedding_and_usage(
        self, text: str
    ) -> Tuple[List[float], Optional[Dict]]:
        return self.get_embedding_and_usage(text)


def get_embedder() -> Embedder:
    provider = os.getenv("EMBEDDER_PROVIDER", "local").strip().lower()

    if provider == "openai":
        from agno.knowledge.embedder.openai import OpenAIEmbedder

        return OpenAIEmbedder(
            id=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    if provider in {"local", "hash", "local_hash"}:
        return LocalHashEmbedder(
            dimensions=int(os.getenv("EMBEDDER_DIMENSIONS", "1536"))
        )

    raise ValueError(f"EMBEDDER_PROVIDER nao suportado: {provider}")
