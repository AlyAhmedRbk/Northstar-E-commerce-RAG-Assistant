from app import create_app


def test_home_page_loads():
    app = create_app()
    app.config["TESTING"] = True

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"Northstar" in response.data
    assert b"chat-launcher" in response.data
    assert b"chat-panel" in response.data


def test_chat_rejects_missing_question():
    app = create_app()
    app.config["TESTING"] = True

    response = app.test_client().post("/api/chat/", json={})

    assert response.status_code == 400


def test_chat_rejects_invalid_json():
    app = create_app()
    app.config["TESTING"] = True

    response = app.test_client().post(
        "/api/chat/",
        data="not-json",
        content_type="application/json",
    )

    assert response.status_code == 400


def test_chat_returns_grounded_response(monkeypatch):
    from app.routes import chat as chat_module

    def fake_answer_question(question):
        return {
            "answer": "The HP EliteBook Laptop costs 850 USD.",
            "sources": [{
                "reference": "S1",
                "filename": "sample_products.txt",
                "section": "PRODUCT: HP EliteBook Laptop",
                "chunk_index": 0,
                "similarity": 0.85,
            }],
            "retrieved_chunks": 1,
            "grounded": True,
        }

    monkeypatch.setattr(
        chat_module,
        "answer_question",
        fake_answer_question,
    )

    app = create_app()
    app.config["TESTING"] = True

    response = app.test_client().post(
        "/api/chat/",
        json={"question": "What is the price of the HP EliteBook?"},
    )

    assert response.status_code == 200

    result = response.get_json()

    assert result["status"] == "success"
    assert result["grounded"] is True
    assert "850 USD" in result["answer"]
    assert result["sources"][0]["filename"] == "sample_products.txt"


def test_customer_cannot_access_document_management():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    assert client.get("/api/documents/").status_code == 404
    assert client.post("/api/documents/upload").status_code == 404
    assert client.post(
        "/api/documents/search",
        json={"query": "laptop"},
    ).status_code == 404
    assert client.delete(
        "/api/documents/example-id",
    ).status_code == 404
