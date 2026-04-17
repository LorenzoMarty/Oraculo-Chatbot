from agno.knowledge import Knowledge
from agno.vectordb.qdrant import Qdrant

from core.loaders.file_loader import load_file

vector_db = Qdrant(
    collection="oraculo",
    url="http://localhost:6333",
)

knowledge = Knowledge(vector_db=vector_db)


def split_text(text, size=1000):
    return [text[i : i + size] for i in range(0, len(text), size)]


def ingest_file(tipo, caminho):
    texto = load_file(tipo, caminho)

    if not texto:
        raise Exception("Documento vazio")

    # limitar tamanho total
    texto = texto[:20000]

    chunks = split_text(texto)

    for chunk in chunks:
        knowledge.insert(text=chunk)
