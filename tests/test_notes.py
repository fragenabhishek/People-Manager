"""Tests for notes CRUD and activity feed."""
from conftest import _data, _json


def _make_person(client, name="Test Person"):
    resp = client.post("/api/people", json={"name": name})
    return _json(resp)["data"]["id"]


def _make_note(client, person_id, content="A note", note_type="general"):
    return client.post(
        f"/api/notes/person/{person_id}",
        json={"content": content, "note_type": note_type},
    )


# --- CRUD ---

def test_create_note(auth_client):
    pid = _make_person(auth_client)
    resp = _make_note(auth_client, pid, "Meeting went well", "meeting")
    assert resp.status_code == 201
    note = _json(resp)["data"]
    assert note["content"] == "Meeting went well"
    assert note["note_type"] == "meeting"


def test_create_note_empty_content(auth_client):
    pid = _make_person(auth_client)
    resp = _make_note(auth_client, pid, content="")
    assert resp.status_code in (400, 422)


def test_create_note_invalid_type(auth_client):
    pid = _make_person(auth_client)
    resp = _make_note(auth_client, pid, note_type="invalid_type")
    assert resp.status_code in (201, 400)


def test_get_notes_for_person(auth_client):
    pid = _make_person(auth_client)
    _make_note(auth_client, pid, "First note")
    _make_note(auth_client, pid, "Second note", "call")

    resp = auth_client.get(f"/api/notes/person/{pid}")
    assert resp.status_code == 200
    notes = _data(resp)
    assert len(notes) == 2


def test_delete_note(auth_client):
    pid = _make_person(auth_client)
    note_id = _json(_make_note(auth_client, pid))["data"]["id"]

    resp = auth_client.delete(f"/api/notes/{note_id}")
    assert resp.status_code == 200

    resp = auth_client.get(f"/api/notes/person/{pid}")
    assert len(_data(resp)) == 0


def test_delete_nonexistent_note(auth_client):
    resp = auth_client.delete("/api/notes/does-not-exist")
    assert resp.status_code == 404


# --- Activity feed ---

def test_activity_feed(auth_client):
    pid = _make_person(auth_client)
    _make_note(auth_client, pid, "Activity note")
    resp = auth_client.get("/api/notes/activity")
    assert resp.status_code == 200
    assert len(_data(resp)) >= 1


def test_activity_feed_limit(auth_client):
    pid = _make_person(auth_client)
    for i in range(5):
        _make_note(auth_client, pid, f"Note {i}")

    resp = auth_client.get("/api/notes/activity?limit=3")
    assert resp.status_code == 200
    assert len(_data(resp)) == 3


# --- Relationship scoring ---

def test_notes_update_relationship_score(auth_client):
    pid = _make_person(auth_client)
    for i in range(3):
        _make_note(auth_client, pid, f"Interaction {i}")

    resp = auth_client.get(f"/api/people/{pid}")
    person = _data(resp)
    assert person["interaction_count"] >= 3
    assert person["relationship_score"] > 0
