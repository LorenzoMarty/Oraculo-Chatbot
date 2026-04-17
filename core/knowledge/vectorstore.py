import os

from agno.vectordb.qdrant import Qdrant
from core.knowledge.embeddings import get_embedder
from agno.knowledge import Knowledge
from qdrant_client import models

vector_db = Qdrant(
    collection=os.getenv("QDRANT_COLLECTION", "oraculo"),
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    embedder=get_embedder(),
)

knowledge = Knowledge(vector_db=vector_db)


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
