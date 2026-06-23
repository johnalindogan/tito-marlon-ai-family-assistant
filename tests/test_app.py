from fastapi.testclient import TestClient
import pytest

from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.service.extract_memories", lambda message: [])
    monkeypatch.setattr(
        "app.service.generate_reply",
        lambda sender_id, message, recent_chat, memory: (
            "Hi, ako si Tito Marlon. Naka-receive ako ng message mo. "
            "Inaayos pa ang full AI memory ko, pero nandito ako para tumulong."
        ),
    )


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_message_returns_fallback_reply() -> None:
    response = client.post(
        "/message",
        json={"sender_id": "sender-1", "message": "Kumusta?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "reply" in body
    assert body["memories_saved"] == []
    assert "Tito Marlon" in body["reply"]


def test_message_rejects_blank_text() -> None:
    response = client.post(
        "/message",
        json={"sender_id": "sender-1", "message": "   "},
    )

    assert response.status_code == 422
