"""
Shared pytest fixtures for the People Manager test suite (FastAPI).
"""
import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("FLASK_DEBUG", "True")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-32chars!")

from main import create_app


@pytest.fixture()
def app(tmp_path):
    """Create a fresh FastAPI app with isolated JSON storage for each test."""
    data_file = str(tmp_path / "data.json")
    users_file = str(tmp_path / "users.json")
    notes_file = str(tmp_path / "notes.json")

    from config import Config
    orig = {
        "DATA_FILE": Config.DATA_FILE,
        "USERS_FILE": Config.USERS_FILE,
        "NOTES_FILE": Config.NOTES_FILE,
        "USE_MONGODB": Config.USE_MONGODB,
        "USE_SQL": Config.USE_SQL,
        "DATABASE_URL": Config.DATABASE_URL,
    }

    Config.DATA_FILE = data_file
    Config.USERS_FILE = users_file
    Config.NOTES_FILE = notes_file
    Config.USE_MONGODB = False
    Config.USE_SQL = False
    Config.DATABASE_URL = None

    application = create_app()
    application.state.testing = True

    yield application

    for k, v in orig.items():
        setattr(Config, k, v)


@pytest.fixture()
def client(app):
    return TestClient(app)


@pytest.fixture()
def auth_client(client):
    """A test client that is already registered and logged in (via session)."""
    client.post("/register", data={
        "username": "testuser",
        "password": "password123",
        "confirm_password": "password123",
    })
    client.post("/login", data={
        "username": "testuser",
        "password": "password123",
    })
    return client


def _json(resp):
    return resp.json()


def _data(resp):
    body = resp.json()
    if isinstance(body, dict) and "data" in body:
        return body["data"]
    return body
