from app.ingestion.indexer import process_document


def test_process_text_document(tmp_path):
    document = tmp_path / "products.txt"

    document.write_text(
        "PRODUCT CATALOG\n\n"
        "Product Name: Laptop\n"
        "Price: 1200 USD\n"
        "Availability: In Stock\n\n"
        "PRODUCT POLICIES\n\n"
        "Returns are accepted within 30 days.",
        encoding="utf-8",
    )

    result = process_document(
        path=document,
        original_filename="products.txt",
    )

    assert result["total_chunks"] > 0
    assert result["total_characters"] > 0
    assert result["document"]["file_type"] == "txt"
    assert result["document"]["original_filename"] == "products.txt"

    for chunk in result["chunks"]:
        assert chunk["content"]
        assert chunk["metadata"]["document_id"] == (
            result["document"]["document_id"]
        )
