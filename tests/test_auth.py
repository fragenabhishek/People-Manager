"""Tests for authentication (register, login, logout)."""
from conftest import _json


def test_register_success(client):
    resp = client.post('/register', data={
        'username': 'newuser',
        'password': 'secret123',
        'confirm_password': 'secret123',
    })
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_register_empty_username(client):
    resp = client.post('/register', data={
        'username': '',
        'password': 'secret123',
        'confirm_password': 'secret123',
    })
    assert resp.status_code == 200
    assert b'required' in resp.data.lower() or b'error' in resp.data.lower()


def test_register_short_password(client):
    resp = client.post('/register', data={
        'username': 'newuser',
        'password': '123',
        'confirm_password': '123',
    })
    assert resp.status_code == 200
    assert b'at least' in resp.data.lower() or b'character' in resp.data.lower()


def test_register_password_mismatch(client):
    resp = client.post('/register', data={
        'username': 'newuser',
        'password': 'secret123',
        'confirm_password': 'different',
    })
    assert resp.status_code == 200
    assert b'match' in resp.data.lower()


def test_register_duplicate_username(client):
    client.post('/register', data={
        'username': 'dupuser',
        'password': 'secret123',
        'confirm_password': 'secret123',
    })
    resp = client.post('/register', data={
        'username': 'dupuser',
        'password': 'secret123',
        'confirm_password': 'secret123',
    })
    assert resp.status_code == 200
    assert b'exists' in resp.data.lower()


def test_login_success(client):
    client.post('/register', data={
        'username': 'loginuser',
        'password': 'secret123',
        'confirm_password': 'secret123',
    })
    resp = client.post('/login', data={
        'username': 'loginuser',
        'password': 'secret123',
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_login_wrong_password(client):
    client.post('/register', data={
        'username': 'loginuser2',
        'password': 'secret123',
        'confirm_password': 'secret123',
    })
    resp = client.post('/login', data={
        'username': 'loginuser2',
        'password': 'wrongpassword',
    })
    assert b'invalid' in resp.data.lower()


def test_logout(auth_client):
    resp = auth_client.get('/logout')
    assert resp.status_code == 302

    resp = auth_client.get('/api/people', headers={'Accept': 'application/json'})
    assert resp.status_code == 401
