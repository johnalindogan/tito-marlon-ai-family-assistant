from fastapi.testclient import TestClient
import pytest

from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    class NoDatabaseSession:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    monkeypatch.setattr("app.service.database.session_scope", lambda: NoDatabaseSession())
    monkeypatch.setattr("app.service.extract_memories", lambda message: [])
    monkeypatch.setattr(
        "app.service.generate_reply",
        lambda sender_id, message, image_urls, family_member, messenger_contact, recent_chat, memory: (
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
    assert body["outbound_image_urls"] == []
    assert body["identified_family_member"] is None
    assert body["messenger_contact"] is None
    assert "Tito Marlon" in body["reply"]


def test_message_accepts_messenger_profile() -> None:
    response = client.post(
        "/message",
        json={
            "sender_id": "sender-1",
            "message": "Kumusta?",
            "messenger_profile": {
                "first_name": "Juan",
                "last_name": "Dela Cruz",
                "profile_pic": "https://example.com/profile.jpg",
                "locale": "en_US",
                "timezone": 8,
            },
        },
    )

    assert response.status_code == 200


def test_message_rejects_blank_text() -> None:
    response = client.post(
        "/message",
        json={"sender_id": "sender-1", "message": "   "},
    )

    assert response.status_code == 422


def test_message_accepts_image_without_text() -> None:
    response = client.post(
        "/message",
        json={
            "sender_id": "sender-1",
            "image_urls": ["https://example.com/photo.jpg"],
        },
    )

    assert response.status_code == 200
    assert "reply" in response.json()


def test_system_prompt_allows_photos() -> None:
    from app.prompts import SYSTEM_PROMPT

    assert "Photos are allowed" in SYSTEM_PROMPT
    assert "Do not claim photos are forbidden" in SYSTEM_PROMPT


def test_user_content_includes_image_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    from app import ai

    monkeypatch.setattr(ai, "_download_image_data_url", lambda image_url: None)

    content = ai._user_content("Ano ito?", ["https://example.com/photo.jpg"])

    assert isinstance(content, list)
    assert content[0] == {"type": "text", "text": "Ano ito?"}
    assert content[1] == {
        "type": "image_url",
        "image_url": {"url": "https://example.com/photo.jpg"},
    }


def test_running_photo_request_returns_outbound_images() -> None:
    response = client.post(
        "/message",
        json={
            "sender_id": "sender-1",
            "message": "Sendan mo ako ng photos tungkol sa 10k run outfit",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert len(body["outbound_image_urls"]) == 3
    assert all(url.startswith("https://") for url in body["outbound_image_urls"])


def test_family_member_context_formatting() -> None:
    from app.ai import _format_family_member

    context = _format_family_member(
        {
            "member_key": "nelon_alindogan",
            "full_name": "Nelon Alindogan",
            "preferred_name": "Papa Nelon",
            "relationship_label": "Papa Nelon / Grandpa Nelon",
            "aliases": ["Papa Nelon", "Grandpa Nelon"],
            "facebook_url": "https://www.facebook.com/leaderalindogan",
        }
    )

    assert "Papa Nelon" in context
    assert "Do not ask this person who they are" in context


def test_messenger_contact_context_formatting() -> None:
    from app.ai import _format_messenger_contact

    context = _format_messenger_contact(
        {
            "sender_id": "sender-1",
            "first_name": "Juan",
            "last_name": "Dela Cruz",
            "profile_pic": "https://example.com/profile.jpg",
            "locale": "en_US",
            "timezone": 8,
            "family_member_key": None,
        }
    )

    assert "Juan Dela Cruz" in context
    assert "do not call them a family role" in context


def test_messenger_profile_rejects_invalid_profile_pic() -> None:
    response = client.post(
        "/message",
        json={
            "sender_id": "sender-1",
            "message": "Kumusta?",
            "messenger_profile": {
                "first_name": "Juan",
                "profile_pic": "not-a-url",
            },
        },
    )

    assert response.status_code == 422
