from app.retrieval.vector_store import get_collection


def search_documents(
    query: str,
    n_results: int = 5,
    document_id: str | None = None,
) -> list[dict]:

    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    if not 1 <= n_results <= 10:
        raise ValueError("n_results must be between 1 and 10.")

    collection = get_collection()

    total_documents = collection.count()

    if total_documents == 0:
        return []

    number_of_results = min(n_results, total_documents)

    filters = None

    if document_id:
        filters = {
            "document_id": document_id,
        }

    results = collection.query(
        query_texts=[query],
        n_results=number_of_results,
        where=filters,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    matches = []

    for content, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        similarity = 1.0 - float(distance)

        matches.append({
            "content": content,
            "metadata": metadata,
            "distance": round(float(distance), 4),
            "similarity": round(similarity, 4),
        })

    return matches
