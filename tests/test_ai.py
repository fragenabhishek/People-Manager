"""Tests for AI endpoints (graceful degradation without API key)."""
import json

from conftest import _json


def _make_person(client, name="AI Test Person"):
    resp = client.post('/api/people',
                       data=json.dumps({"name": name}),
                       content_type='application/json')
    return _json(resp)['data']['id']


def test_blueprint_returns_503_without_key(auth_client):
    pid = _make_person(auth_client)
    resp = auth_client.post(f'/api/people/{pid}/summary', content_type='application/json')
    assert resp.status_code == 503
    assert 'configured' in _json(resp).get('error', '').lower() or 'api_key' in _json(resp).get('error', '').lower()


def test_ask_returns_503_without_key(auth_client):
    _make_person(auth_client)
    resp = auth_client.post('/api/ask',
                            data=json.dumps({"question": "Who works in tech?"}),
                            content_type='application/json')
    assert resp.status_code == 503


def test_suggest_tags_returns_503_without_key(auth_client):
    pid = _make_person(auth_client)
    resp = auth_client.post(f'/api/people/{pid}/suggest-tags', content_type='application/json')
    assert resp.status_code == 503


def test_ask_empty_question(auth_client):
    _make_person(auth_client)
    resp = auth_client.post('/api/ask',
                            data=json.dumps({"question": ""}),
                            content_type='application/json')
    assert resp.status_code in (400, 503)
