from pathlib import Path

from app.ingestion.chunk_validator import validate_chunks
from app.ingestion.chunker import chunk_sections
from app.ingestion.extractors import extract_document
from app.ingestion.metadata_builder import (
    build_chunk_metadata,
    build_document_metadata,
)
from app.ingestion.structure_parser import parse_document_structure
from app.ingestion.text_cleaner import clean_text


def process_document(
    path: Path,
    original_filename: str,
) -> dict:

    raw_text = extract_document(path)

    cleaned_text = clean_text(raw_text)

    if not cleaned_text:
        raise ValueError(
            "The document contains no extractable text."
        )

    sections = parse_document_structure(cleaned_text)

    if not sections:
        raise ValueError(
            "Unable to identify meaningful document content."
        )

    chunks = chunk_sections(sections)
    chunks = validate_chunks(chunks)

    document_metadata = build_document_metadata(
        path,
        original_filename,
    )

    processed_chunks = []

    for chunk in chunks:
        processed_chunks.append({
            "content": chunk["content"],
            "metadata": build_chunk_metadata(
                document_metadata,
                chunk,
            ),
        })

    return {
        "document": document_metadata,
        "total_characters": len(cleaned_text),
        "total_tokens": sum(
            item["metadata"]["token_count"]
            for item in processed_chunks
        ),
        "total_chunks": len(processed_chunks),
        "chunks": processed_chunks,
    }
