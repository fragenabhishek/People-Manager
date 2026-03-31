"""Tests for AI endpoints (graceful degradation without API key)."""
from conftest import _json


def _make_person(client, name="AI Test Person"):
    resp = client.post("/api/people", json={"name": name})
    return _json(resp)["data"]["id"]


def test_blueprint_returns_503_without_key(auth_client):
    pid = _make_person(auth_client)
    resp = auth_client.post(f"/api/people/{pid}/summary")
    assert resp.status_code == 503
    assert "configured" in _json(resp).get("error", "").lower() or "api_key" in _json(resp).get("error", "").lower()


def test_ask_returns_503_without_key(auth_client):
    _make_person(auth_client)
    resp = auth_client.post("/api/ask", json={"question": "Who works in tech?"})
    assert resp.status_code == 503


def test_suggest_tags_returns_503_without_key(auth_client):
    pid = _make_person(auth_client)
    resp = auth_client.post(f"/api/people/{pid}/suggest-tags")
    assert resp.status_code == 503


def test_ask_empty_question(auth_client):
    _make_person(auth_client)
    resp = auth_client.post("/api/ask", json={"question": ""})
    assert resp.status_code in (400, 422, 503)
