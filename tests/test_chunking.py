from app.ingestion.chunker import chunk_text, count_tokens


def test_chunk_text_returns_chunks():
    text = "Product information. " * 500

    chunks = chunk_text(text, chunk_size=100, overlap=20)

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)


def test_chunks_respect_token_limit():
    text = "E-commerce product information. " * 500

    chunks = chunk_text(text, chunk_size=100, overlap=20)

    for chunk in chunks:
        assert count_tokens(chunk) <= 100


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []
