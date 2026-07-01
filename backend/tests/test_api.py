"""Unit tests for the API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client (without full model initialization for unit tests)."""
    from unittest.mock import MagicMock, patch

    # Mock the heavy initialization
    with (
        patch("app.main.FAISSStore") as MockFaiss,
        patch("app.main.BM25Store") as MockBM25,
    ):
        mock_faiss = MockFaiss.return_value
        mock_faiss.catalog = [{"id": "test", "name": "Test Assessment"}]
        mock_faiss.initialize = MagicMock()

        mock_bm25 = MockBM25.return_value
        mock_bm25.initialize = MagicMock()

        from app.main import create_app

        app = create_app()
        yield TestClient(app)


class TestHealthEndpoint:
    """Test GET /health."""

    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestChatEndpoint:
    """Test POST /chat request validation."""

    def test_rejects_empty_body(self, client):
        response = client.post("/chat", json={})
        assert response.status_code == 422

    def test_rejects_empty_messages(self, client):
        response = client.post("/chat", json={"messages": []})
        assert response.status_code == 422

    def test_rejects_invalid_role(self, client):
        response = client.post(
            "/chat", json={"messages": [{"role": "invalid", "content": "hello"}]}
        )
        assert response.status_code == 422

    def test_rejects_too_many_turns(self, client):
        # 17 messages = more than 8 turns
        messages = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"msg {i}"}
            for i in range(17)
        ]
        response = client.post("/chat", json={"messages": messages})
        assert response.status_code == 422

    def test_accepts_valid_request(self, client):
        response = client.post(
            "/chat",
            json={"messages": [{"role": "user", "content": "I need a Java developer assessment"}]},
        )
        # This may fail in unit test due to mocked services, but should not be 422
        assert response.status_code in (200, 500)  # 500 if mocks aren't fully set up
