"""Tests for people/contacts CRUD, search, tags, and follow-ups."""
from fastapi.testclient import TestClient

from conftest import _data, _json


def _create_person(client, name="John Doe", **overrides):
    data = {"name": name, "email": "john@example.com", "company": "Acme", **overrides}
    return client.post("/api/people", json=data)


# --- CRUD ---

def test_create_person(auth_client):
    resp = _create_person(auth_client)
    assert resp.status_code == 201
    body = _json(resp)
    assert body["success"] is True
    assert body["data"]["name"] == "John Doe"
    assert body["data"]["id"] is not None


def test_create_person_empty_name(auth_client):
    resp = _create_person(auth_client, name="")
    assert resp.status_code in (400, 422)


def test_get_all_people(auth_client):
    _create_person(auth_client, name="Alice")
    _create_person(auth_client, name="Bob")
    resp = auth_client.get("/api/people")
    assert resp.status_code == 200
    assert len(_data(resp)) == 2


def test_get_person_by_id(auth_client):
    pid = _json(_create_person(auth_client))["data"]["id"]
    resp = auth_client.get(f"/api/people/{pid}")
    assert resp.status_code == 200
    assert _data(resp)["name"] == "John Doe"


def test_get_nonexistent_person(auth_client):
    resp = auth_client.get("/api/people/does-not-exist")
    assert resp.status_code == 404


def test_update_person(auth_client):
    pid = _json(_create_person(auth_client))["data"]["id"]
    resp = auth_client.put(f"/api/people/{pid}", json={"name": "Jane Doe", "company": "NewCo"})
    assert resp.status_code == 200
    updated = _data(resp)
    assert updated["name"] == "Jane Doe"
    assert updated["company"] == "NewCo"
    assert updated["email"] == "john@example.com"


def test_delete_person(auth_client):
    pid = _json(_create_person(auth_client))["data"]["id"]
    resp = auth_client.delete(f"/api/people/{pid}")
    assert resp.status_code == 200
    resp = auth_client.get(f"/api/people/{pid}")
    assert resp.status_code == 404


# --- Search ---

def test_search_by_name(auth_client):
    _create_person(auth_client, name="Searchable Person")
    resp = auth_client.get("/api/people/search/Searchable")
    assert resp.status_code == 200
    assert len(_data(resp)) >= 1


def test_search_no_results(auth_client):
    resp = auth_client.get("/api/people/search/zzzzzzzzz")
    assert resp.status_code == 200
    assert len(_data(resp)) == 0


# --- Tags ---

def test_add_and_remove_tags(auth_client):
    pid = _json(_create_person(auth_client))["data"]["id"]
    resp = auth_client.post(f"/api/people/{pid}/tags", json={"tags": ["mentor", "vip"]})
    assert resp.status_code == 200
    tags = _data(resp)["tags"]
    assert "mentor" in tags
    assert "vip" in tags

    resp = auth_client.delete(f"/api/people/{pid}/tags/vip")
    assert resp.status_code == 200
    assert "vip" not in _data(resp)["tags"]


def test_get_all_tags(auth_client):
    _create_person(auth_client, tags=["alpha", "beta"])
    resp = auth_client.get("/api/people/tags")
    assert resp.status_code == 200
    tags = _data(resp)
    assert "alpha" in tags
    assert "beta" in tags


def test_filter_by_tag(auth_client):
    _create_person(auth_client, name="Tagged", tags=["special"])
    _create_person(auth_client, name="Untagged")
    resp = auth_client.get("/api/people?tag=special")
    assert resp.status_code == 200
    results = _data(resp)
    assert len(results) == 1
    assert results[0]["name"] == "Tagged"


# --- Follow-ups ---

def test_set_and_complete_followup(auth_client):
    pid = _json(_create_person(auth_client))["data"]["id"]
    resp = auth_client.put(f"/api/people/{pid}/followup", json={"date": "2026-03-20", "frequency_days": 7})
    assert resp.status_code == 200
    assert _data(resp)["next_follow_up"] == "2026-03-20"
    assert _data(resp)["follow_up_frequency_days"] == 7

    resp = auth_client.post(f"/api/people/{pid}/followup/complete")
    assert resp.status_code == 200
    completed = _data(resp)
    assert completed["next_follow_up"] != "2026-03-20"
    assert completed["next_follow_up"] != ""


def test_get_due_followups(auth_client):
    _create_person(auth_client, name="Due", next_follow_up="2020-01-01")
    _create_person(auth_client, name="Future", next_follow_up="2099-12-31")
    resp = auth_client.get("/api/people/followups")
    assert resp.status_code == 200
    due = _data(resp)
    names = [p["name"] for p in due]
    assert "Due" in names
    assert "Future" not in names


# --- Dashboard ---

def test_dashboard_stats(auth_client):
    _create_person(auth_client, name="A")
    _create_person(auth_client, name="B")
    resp = auth_client.get("/api/people/dashboard/stats")
    assert resp.status_code == 200
    stats = _data(resp)
    assert stats["total_contacts"] == 2
    assert "status_counts" in stats
    assert "tag_counts" in stats


# --- Auth isolation ---

def test_data_isolation(app):
    """Two users should not see each other's contacts."""
    c1 = TestClient(app)
    c2 = TestClient(app)

    c1.post("/register", data={"username": "user1", "password": "pass1234", "confirm_password": "pass1234"})
    c1.post("/login", data={"username": "user1", "password": "pass1234"})
    _create_person(c1, name="User1 Contact")

    c2.post("/register", data={"username": "user2", "password": "pass1234", "confirm_password": "pass1234"})
    c2.post("/login", data={"username": "user2", "password": "pass1234"})

    resp = c2.get("/api/people")
    assert len(_data(resp)) == 0
