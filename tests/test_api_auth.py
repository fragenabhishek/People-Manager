"""Tests for /api/auth/* JWT-based endpoints."""
import json

from conftest import _data, _json


def _register(client, username="apiuser", password="secret123", email="api@test.com"):
    return client.post('/api/auth/register',
                       data=json.dumps({
                           "username": username,
                           "password": password,
                           "confirm_password": password,
                           "email": email,
                       }),
                       content_type='application/json')


def _login(client, username="apiuser", password="secret123"):
    return client.post('/api/auth/login',
                       data=json.dumps({"username": username, "password": password}),
                       content_type='application/json')


def _auth_header(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# --- Register ---

def test_api_register(client):
    resp = _register(client)
    assert resp.status_code == 201
    body = _json(resp)
    assert body['success'] is True
    assert 'access_token' in body['data']
    assert 'refresh_token' in body['data']
    assert body['data']['user']['username'] == 'apiuser'


def test_api_register_duplicate(client):
    _register(client)
    resp = _register(client)
    assert resp.status_code == 400


def test_api_register_short_password(client):
    resp = _register(client, password="ab")
    assert resp.status_code == 400


# --- Login ---

def test_api_login(client):
    _register(client)
    resp = _login(client)
    assert resp.status_code == 200
    data = _data(resp)
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['username'] == 'apiuser'


def test_api_login_wrong_password(client):
    _register(client)
    resp = _login(client, password="wrong")
    assert resp.status_code == 401


def test_api_login_missing_fields(client):
    resp = client.post('/api/auth/login',
                       data=json.dumps({"username": "", "password": ""}),
                       content_type='application/json')
    assert resp.status_code == 400


# --- Me ---

def test_api_me(client):
    _register(client)
    token = _data(_login(client))['access_token']

    resp = client.get('/api/auth/me', headers=_auth_header(token))
    assert resp.status_code == 200
    assert _data(resp)['username'] == 'apiuser'


def test_api_me_no_token(client):
    resp = client.get('/api/auth/me')
    assert resp.status_code == 401


def test_api_me_bad_token(client):
    resp = client.get('/api/auth/me', headers=_auth_header("invalid.token.here"))
    assert resp.status_code == 401


# --- Refresh ---

def test_api_refresh(client):
    _register(client)
    tokens = _data(_login(client))

    resp = client.post('/api/auth/refresh',
                       data=json.dumps({"refresh_token": tokens['refresh_token']}),
                       content_type='application/json')
    assert resp.status_code == 200
    new_tokens = _data(resp)
    assert 'access_token' in new_tokens
    assert 'refresh_token' in new_tokens
    assert new_tokens['token_type'] == 'bearer'


def test_api_refresh_reuse_rejected(client):
    _register(client)
    tokens = _data(_login(client))
    refresh = tokens['refresh_token']

    client.post('/api/auth/refresh',
                data=json.dumps({"refresh_token": refresh}),
                content_type='application/json')

    resp = client.post('/api/auth/refresh',
                       data=json.dumps({"refresh_token": refresh}),
                       content_type='application/json')
    assert resp.status_code == 401


def test_api_refresh_missing(client):
    resp = client.post('/api/auth/refresh',
                       data=json.dumps({}),
                       content_type='application/json')
    assert resp.status_code == 400


# --- Logout ---

def test_api_logout(client):
    _register(client)
    tokens = _data(_login(client))
    access = tokens['access_token']
    refresh = tokens['refresh_token']

    resp = client.post('/api/auth/logout',
                       data=json.dumps({"refresh_token": refresh}),
                       headers=_auth_header(access))
    assert resp.status_code == 200

    resp = client.post('/api/auth/refresh',
                       data=json.dumps({"refresh_token": refresh}),
                       content_type='application/json')
    assert resp.status_code == 401


# --- Change Password ---

def test_api_change_password(client):
    _register(client, password="oldpass123")
    token = _data(_login(client, password="oldpass123"))['access_token']

    resp = client.post('/api/auth/change-password',
                       data=json.dumps({
                           "current_password": "oldpass123",
                           "new_password": "newpass456",
                           "confirm_password": "newpass456",
                       }),
                       headers=_auth_header(token))
    assert resp.status_code == 200

    resp = _login(client, password="newpass456")
    assert resp.status_code == 200


def test_api_change_password_wrong_current(client):
    _register(client)
    token = _data(_login(client))['access_token']

    resp = client.post('/api/auth/change-password',
                       data=json.dumps({
                           "current_password": "wrong",
                           "new_password": "newpass456",
                           "confirm_password": "newpass456",
                       }),
                       headers=_auth_header(token))
    assert resp.status_code == 400


# --- Forgot / Reset Password ---

def test_api_forgot_and_reset_password(client):
    _register(client, email="user@test.com")

    resp = client.post('/api/auth/forgot-password',
                       data=json.dumps({"email": "user@test.com"}),
                       content_type='application/json')
    assert resp.status_code == 200
    reset_token = _data(resp).get('reset_token')
    assert reset_token is not None

    resp = client.post('/api/auth/reset-password',
                       data=json.dumps({"token": reset_token, "new_password": "brandnew123"}),
                       content_type='application/json')
    assert resp.status_code == 200

    resp = _login(client, password="brandnew123")
    assert resp.status_code == 200


def test_api_forgot_unknown_email(client):
    resp = client.post('/api/auth/forgot-password',
                       data=json.dumps({"email": "nobody@nowhere.com"}),
                       content_type='application/json')
    assert resp.status_code == 200  # no information leak


def test_api_reset_bad_token(client):
    resp = client.post('/api/auth/reset-password',
                       data=json.dumps({"token": "invalid", "new_password": "newpass123"}),
                       content_type='application/json')
    assert resp.status_code == 401


# --- JWT works with existing API routes ---

def test_jwt_works_with_people_api(client):
    """Verify the dual-auth middleware lets JWT tokens access regular API routes."""
    _register(client)
    token = _data(_login(client))['access_token']

    resp = client.post('/api/people',
                       data=json.dumps({"name": "JWT Contact"}),
                       headers=_auth_header(token))
    assert resp.status_code == 201
    assert _json(resp)['data']['name'] == 'JWT Contact'

    resp = client.get('/api/people', headers=_auth_header(token))
    assert resp.status_code == 200
    assert len(_data(resp)) == 1
