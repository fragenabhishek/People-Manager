"""
Integration tests that run the full FastAPI app with SQLite as the database.
Proves that all API endpoints work identically with the SQL backend.
"""
import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("FLASK_DEBUG", "True")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-32chars!")

from conftest import _data, _json
from main import create_app


@pytest.fixture()
def sql_app():
    from config import Config
    orig = {
        "USE_SQL": Config.USE_SQL,
        "DATABASE_URL": Config.DATABASE_URL,
        "USE_MONGODB": Config.USE_MONGODB,
    }
    Config.DATABASE_URL = "sqlite:///:memory:"
    Config.USE_SQL = True
    Config.USE_MONGODB = False

    application = create_app()
    application.state.testing = True
    yield application

    for k, v in orig.items():
        setattr(Config, k, v)


@pytest.fixture()
def sql_client(sql_app):
    return TestClient(sql_app)


@pytest.fixture()
def sql_auth_client(sql_client):
    sql_client.post("/register", data={"username": "sqluser", "password": "password123", "confirm_password": "password123"})
    sql_client.post("/login", data={"username": "sqluser", "password": "password123"})
    return sql_client


def test_health_reports_postgresql(sql_client):
    data = sql_client.get("/health").json()
    assert data["storage"] == "postgresql"


def test_register_login_flow(sql_client):
    resp = sql_client.post("/register", data={"username": "newuser", "password": "pass123", "confirm_password": "pass123"}, follow_redirects=False)
    assert resp.status_code == 303
    resp = sql_client.post("/login", data={"username": "newuser", "password": "pass123"}, follow_redirects=False)
    assert resp.status_code == 303


def test_crud_people(sql_auth_client):
    resp = sql_auth_client.post("/api/people", json={"name": "SQL Contact", "company": "TestCo"})
    assert resp.status_code == 201
    person_id = _data(resp)["id"]

    resp = sql_auth_client.get("/api/people")
    assert len(_data(resp)) == 1

    resp = sql_auth_client.put(f"/api/people/{person_id}", json={"name": "Updated", "company": "NewCo"})
    assert resp.status_code == 200
    assert _data(resp)["company"] == "NewCo"

    resp = sql_auth_client.delete(f"/api/people/{person_id}")
    assert resp.status_code == 200


def test_notes_crud(sql_auth_client):
    person_id = _data(sql_auth_client.post("/api/people", json={"name": "Note Target"}))["id"]
    resp = sql_auth_client.post(f"/api/notes/person/{person_id}", json={"content": "Hello from SQL", "note_type": "meeting"})
    assert resp.status_code == 201
    note_id = _data(resp)["id"]

    resp = sql_auth_client.get(f"/api/notes/person/{person_id}")
    assert len(_data(resp)) == 1

    resp = sql_auth_client.delete(f"/api/notes/{note_id}")
    assert resp.status_code == 200


def test_search(sql_auth_client):
    sql_auth_client.post("/api/people", json={"name": "Alice Wonderland", "company": "MagicCorp"})
    sql_auth_client.post("/api/people", json={"name": "Bob Builder"})
    resp = sql_auth_client.get("/api/people/search/alice")
    assert resp.status_code == 200
    assert len(_data(resp)) == 1


def test_tags(sql_auth_client):
    sql_auth_client.post("/api/people", json={"name": "Tagged", "tags": ["vip", "friend"]})
    tags = _data(sql_auth_client.get("/api/people/tags"))
    assert "vip" in tags
    assert "friend" in tags
    resp = sql_auth_client.get("/api/people?tag=vip")
    assert len(_data(resp)) == 1


def test_dashboard_stats(sql_auth_client):
    sql_auth_client.post("/api/people", json={"name": "D1"})
    resp = sql_auth_client.get("/api/people/dashboard/stats")
    assert resp.status_code == 200
    assert _data(resp)["total_contacts"] == 1


def test_jwt_with_sql_backend(sql_client):
    resp = sql_client.post("/api/auth/register", json={"username": "jwtuser", "password": "secret123", "confirm_password": "secret123"})
    assert resp.status_code == 201
    token = _data(resp)["access_token"]
    resp = sql_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert _data(resp)["username"] == "jwtuser"
