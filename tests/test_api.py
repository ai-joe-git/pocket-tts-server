"""Tests for HTTP API (health, voices, speech validation)."""

from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "voices_loaded" in data
    assert "timestamp" in data


def test_list_voices_returns_200_and_structure(client: TestClient):
    r = client.get("/v1/audio/voices")
    assert r.status_code == 200
    data = r.json()
    assert "voices" in data
    assert isinstance(data["voices"], list)


def test_speech_requires_input(client: TestClient):
    """POST /v1/audio/speech without body or missing input -> 422."""
    r = client.post("/v1/audio/speech", json={})
    assert r.status_code == 422


def test_speech_with_invalid_voice_returns_400_or_503(client: TestClient):
    """POST with non-existent voice may return 400 or 503 depending on TTS availability."""
    r = client.post(
        "/v1/audio/speech",
        json={"input": "Hello", "voice": "nonexistent-voice-id-12345"},
    )
    # 400 if voice not found, 503 if no TTS at all
    assert r.status_code in (400, 503)


def test_root_returns_html(client: TestClient):
    r = client.get("/")
    assert r.status_code == 200
    assert "html" in r.headers.get("content-type", "").lower() or len(r.text) > 0
