import hashlib
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def calculate_file_hash(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def build_document_metadata(
    path: Path,
    original_filename: str,
) -> dict:

    return {
        "document_id": str(uuid4()),
        "original_filename": original_filename,
        "stored_filename": path.name,
        "file_type": path.suffix.lower().lstrip("."),
        "file_hash": calculate_file_hash(path),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_chunk_metadata(
    document_metadata: dict,
    chunk: dict,
) -> dict:

    return {
        "document_id": document_metadata["document_id"],
        "source": document_metadata["original_filename"],
        "file_type": document_metadata["file_type"],
        "file_hash": document_metadata["file_hash"],
        "section": chunk["section"],
        "chunk_index": chunk["chunk_index"],
        "token_count": chunk["token_count"],
    }
