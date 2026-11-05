import tiktoken

from app.config import Config


_encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_encoding.encode(text))


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:

    chunk_size = chunk_size or Config.CHUNK_SIZE
    overlap = overlap if overlap is not None else Config.CHUNK_OVERLAP

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )

    tokens = _encoding.encode(text)

    if not tokens:
        return []

    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))

        chunk = _encoding.decode(tokens[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end == len(tokens):
            break

        start = end - overlap

    return chunks


def chunk_sections(sections: list[dict]) -> list[dict]:
    result = []

    for section in sections:
        section_name = section["section"]
        content = section["content"]

        chunks = chunk_text(content)

        for chunk_number, chunk in enumerate(chunks):
            result.append({
                "section": section_name,
                "chunk_index": len(result),
                "section_chunk_index": chunk_number,
                "content": chunk,
                "token_count": count_tokens(chunk),
            })

    return result
