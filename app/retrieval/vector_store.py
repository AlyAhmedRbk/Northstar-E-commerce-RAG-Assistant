from functools import lru_cache

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from app.config import Config


@lru_cache(maxsize=1)
def get_chroma_client():
    Config.CHROMA_PERSIST_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    return chromadb.PersistentClient(
        path=str(Config.CHROMA_PERSIST_DIRECTORY)
    )


@lru_cache(maxsize=1)
def get_collection():
    client = get_chroma_client()

    embedding_function = DefaultEmbeddingFunction()

    return client.get_or_create_collection(
        name=Config.CHROMA_COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"},
    )


def index_document(processed_document: dict) -> dict:
    collection = get_collection()

    document = processed_document["document"]
    chunks = processed_document["chunks"]

    document_id = document["document_id"]
    file_hash = document["file_hash"]

    existing = collection.get(
        where={"file_hash": file_hash},
        include=["metadatas"],
    )

    if existing["ids"]:
        existing_metadata = existing["metadatas"][0]

        return {
            "indexed": False,
            "duplicate": True,
            "existing_document_id": existing_metadata["document_id"],
            "message": "This document has already been indexed.",
        }

    batch_size = 100
    indexed_count = 0

    try:
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]

            ids = [
                f"{document_id}:{item['metadata']['chunk_index']}"
                for item in batch
            ]

            texts = [
                item["content"]
                for item in batch
            ]

            metadatas = [
                {
                    **item["metadata"],
                    "created_at": document["created_at"],
                    "stored_filename": document["stored_filename"],
                }
                for item in batch
            ]

            collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
            )

            indexed_count += len(batch)

    except Exception:
        # Roll back any batches already added for this document.
        collection.delete(
            where={"document_id": document_id}
        )
        raise

    return {
        "indexed": True,
        "duplicate": False,
        "document_id": document_id,
        "indexed_chunks": indexed_count,
        "message": "Document indexed successfully.",
    }


def delete_document(document_id: str) -> bool:
    collection = get_collection()

    existing = collection.get(
        where={"document_id": document_id},
        include=["metadatas"],
    )

    if not existing["ids"]:
        return False

    collection.delete(
        where={"document_id": document_id}
    )

    return True


def list_documents() -> list[dict]:
    collection = get_collection()

    result = collection.get(
        include=["metadatas"],
    )

    documents = {}

    for metadata in result["metadatas"]:
        document_id = metadata["document_id"]

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": metadata["source"],
                "file_type": metadata["file_type"],
                "file_hash": metadata["file_hash"],
                "created_at": metadata.get("created_at"),
                "total_chunks": 0,
            }

        documents[document_id]["total_chunks"] += 1

    return sorted(
        documents.values(),
        key=lambda item: item.get("created_at") or "",
        reverse=True,
    )
