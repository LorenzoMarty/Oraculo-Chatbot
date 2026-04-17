import os
import time
from pathlib import Path
from uuid import uuid4

from agno.knowledge import Knowledge
from agno.vectordb.qdrant import Qdrant
from qdrant_client import models

from core.knowledge.embeddings import get_embedder
from core.loaders.file_loader import load_file

vector_db = Qdrant(
    collection=os.getenv("QDRANT_COLLECTION", "oraculo"),
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    embedder=get_embedder(),
)

knowledge = Knowledge(vector_db=vector_db)


def split_text(text, size=1000):
    return [text[i : i + size] for i in range(0, len(text), size)]


def count_document_points(document_id):
    result = vector_db.client.count(
        collection_name=vector_db.collection,
        count_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="meta_data.document_id",
                    match=models.MatchValue(value=document_id),
                )
            ]
        ),
        exact=True,
    )
    return result.count


def ingest_file(tipo, caminho, filename=None, document_id=None):
    texto = load_file(tipo, caminho)

    if not texto:
        raise Exception("Documento vazio")

    source_name = filename or Path(caminho).name
    document_id = document_id or uuid4().hex

    # limitar tamanho total
    texto = texto[:20000]

    chunks = split_text(texto)
    header = f"Arquivo: {source_name}\nTipo: {tipo}\nDocumento ID: {document_id}\n\n"

    for index, chunk in enumerate(chunks, start=1):
        knowledge.insert(
            name=f"{source_name}-chunk-{index}",
            text_content=f"{header}{chunk}",
            metadata={
                "tipo": tipo,
                "chunk": index,
                "filename": source_name,
                "document_id": document_id,
            },
        )

    stored_points = 0

    for _ in range(10):
        stored_points = count_document_points(document_id)

        if stored_points > 0:
            break

        time.sleep(0.2)

    if stored_points == 0:
        raise Exception(
            "Nenhum vetor foi gravado no Qdrant. Verifique o embedder configurado "
            "em EMBEDDER_PROVIDER ou defina OPENAI_API_KEY se usar OpenAI."
        )

    return {
        "document_id": document_id,
        "filename": source_name,
        "chunks": len(chunks),
        "stored_points": stored_points,
    }
