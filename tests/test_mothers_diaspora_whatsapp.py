import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _env_for_tests(monkeypatch):
    # Provide required env vars (dummy values) and disable signature validation
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "test_auth_token")
    monkeypatch.setenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    monkeypatch.setenv("DISABLE_TWILIO_SIGNATURE_VALIDATION", "true")


def _client():
    # Import after env is set
    from modal_deployments.mothers_diaspora_whatsapp import web

    return TestClient(web)


def test_health_ok():
    client = _client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_webhook_text_returns_twiml():
    client = _client()

    resp = client.post(
        "/twilio/whatsapp",
        data={
            "From": "whatsapp:+10000000000",
            "To": "whatsapp:+14155238886",
            "Body": "Hello Sisi Lola",
            "NumMedia": "0",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/xml")
    assert "<Response>" in resp.text
    assert "route=text" in resp.text


def test_webhook_voice_reply_request_text_returns_twiml():
    client = _client()

    resp = client.post(
        "/twilio/whatsapp",
        data={
            "From": "whatsapp:+10000000000",
            "To": "whatsapp:+14155238886",
            "Body": "you fit talk?",
            "NumMedia": "0",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/xml")
    assert "route=text" in resp.text
    assert "intent=voice_reply_request" in resp.text


def test_webhook_voice_returns_twiml():
    client = _client()

    resp = client.post(
        "/twilio/whatsapp",
        data={
            "From": "whatsapp:+10000000000",
            "To": "whatsapp:+14155238886",
            "Body": "",
            "NumMedia": "1",
            "MediaUrl0": "https://example.com/audio.ogg",
            "MediaContentType0": "audio/ogg",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/xml")
    assert "route=voice" in resp.text


def test_webhook_trailing_slash_route_works():
    client = _client()

    resp = client.post(
        "/twilio/whatsapp/",
        data={
            "From": "whatsapp:+10000000000",
            "To": "whatsapp:+14155238886",
            "Body": "Hello Sisi Lola",
            "NumMedia": "0",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/xml")
    assert "route=text" in resp.text
