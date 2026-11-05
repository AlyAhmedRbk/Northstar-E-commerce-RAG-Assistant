from app.config import Config
from app.ingestion.chunker import count_tokens


def validate_chunks(chunks: list[dict]) -> list[dict]:
    valid_chunks = []

    for chunk in chunks:
        content = chunk.get("content", "").strip()

        if not content:
            continue

        actual_tokens = count_tokens(content)

        if actual_tokens > Config.CHUNK_SIZE:
            raise ValueError(
                f"Chunk {chunk.get('chunk_index')} exceeds "
                f"the configured limit: {actual_tokens} tokens."
            )

        chunk["content"] = content
        chunk["token_count"] = actual_tokens

        valid_chunks.append(chunk)

    if not valid_chunks:
        raise ValueError(
            "No usable text was extracted from this document."
        )

    return valid_chunks
