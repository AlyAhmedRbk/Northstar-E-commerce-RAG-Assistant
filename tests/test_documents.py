from app import create_app


def test_document_management_routes_are_not_registered():
    app = create_app()
    app.config["TESTING"] = True

    routes = [
        rule.rule
        for rule in app.url_map.iter_rules()
    ]

    assert not any(
        route.startswith("/api/documents")
        for route in routes
    )

    assert "/api/chat/" in routes
    assert "/" in routes
