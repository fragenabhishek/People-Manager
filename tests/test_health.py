"""Tests for health check and basic app setup."""
from conftest import _json


def test_health_returns_200(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    body = _json(resp)
    assert body['status'] == 'ok'
    assert body['storage'] == 'json'
    assert body['db_connected'] is True


def test_landing_page(client):
    resp = client.get('/')
    assert resp.status_code == 200


def test_dashboard_requires_login(client):
    resp = client.get('/dashboard')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']
