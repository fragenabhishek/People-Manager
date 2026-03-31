"""
Shared pytest fixtures for the People Manager test suite.
"""
import json
import os
import tempfile

import pytest

os.environ.setdefault('FLASK_DEBUG', 'True')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-pytest-32chars!')

from app import create_app


@pytest.fixture()
def app(tmp_path):
    """Create a fresh app instance with isolated JSON storage for each test."""
    data_file = str(tmp_path / "data.json")
    users_file = str(tmp_path / "users.json")
    notes_file = str(tmp_path / "notes.json")

    from config import Config
    orig_data = Config.DATA_FILE
    orig_users = Config.USERS_FILE
    orig_notes = Config.NOTES_FILE
    orig_mongo = Config.USE_MONGODB

    Config.DATA_FILE = data_file
    Config.USERS_FILE = users_file
    Config.NOTES_FILE = notes_file
    Config.USE_MONGODB = False

    application = create_app()
    application.config['TESTING'] = True

    yield application

    Config.DATA_FILE = orig_data
    Config.USERS_FILE = orig_users
    Config.NOTES_FILE = orig_notes
    Config.USE_MONGODB = orig_mongo


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(client):
    """A test client that is already registered and logged in."""
    client.post('/register', data={
        'username': 'testuser',
        'password': 'password123',
        'confirm_password': 'password123',
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123',
    })
    return client


def _json(resp):
    """Parse JSON response body."""
    return resp.get_json(force=True)


def _data(resp):
    """Unwrap APIResponse envelope and return .data."""
    body = _json(resp)
    if isinstance(body, dict) and 'data' in body:
        return body['data']
    return body
