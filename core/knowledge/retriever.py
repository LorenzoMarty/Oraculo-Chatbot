from typing import List

from agno.knowledge.document import Document


def retrieve_context(query: str, top_k: int = 5) -> List[Document]:
    query = query.strip()

    if not query or top_k <= 0:
        return []

    # vectorstore initializes Qdrant on import, so keep this lazy.
    from core.knowledge.vectorstore import vector_db

    results = vector_db.search(query=query, limit=top_k)

    return [document for document in results if document.content]
