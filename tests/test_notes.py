"""Tests for notes CRUD and activity feed."""
import json

from conftest import _data, _json


def _make_person(client, name="Test Person"):
    resp = client.post('/api/people',
                       data=json.dumps({"name": name}),
                       content_type='application/json')
    return _json(resp)['data']['id']


def _make_note(client, person_id, content="A note", note_type="general"):
    return client.post(
        f'/api/notes/person/{person_id}',
        data=json.dumps({"content": content, "note_type": note_type}),
        content_type='application/json',
    )


# --- CRUD ---

def test_create_note(auth_client):
    pid = _make_person(auth_client)
    resp = _make_note(auth_client, pid, "Meeting went well", "meeting")
    assert resp.status_code == 201
    note = _json(resp)['data']
    assert note['content'] == 'Meeting went well'
    assert note['note_type'] == 'meeting'


def test_create_note_empty_content(auth_client):
    pid = _make_person(auth_client)
    resp = _make_note(auth_client, pid, content="")
    assert resp.status_code == 400


def test_create_note_invalid_type(auth_client):
    pid = _make_person(auth_client)
    resp = _make_note(auth_client, pid, note_type="invalid_type")
    assert resp.status_code == 400


def test_get_notes_for_person(auth_client):
    pid = _make_person(auth_client)
    _make_note(auth_client, pid, "First")
    _make_note(auth_client, pid, "Second")

    resp = auth_client.get(f'/api/notes/person/{pid}')
    assert resp.status_code == 200
    notes = _data(resp)
    assert len(notes) == 2


def test_delete_note(auth_client):
    pid = _make_person(auth_client)
    note_id = _json(_make_note(auth_client, pid))['data']['id']

    resp = auth_client.delete(f'/api/notes/{note_id}')
    assert resp.status_code == 200

    resp = auth_client.get(f'/api/notes/person/{pid}')
    assert len(_data(resp)) == 0


def test_delete_nonexistent_note(auth_client):
    resp = auth_client.delete('/api/notes/fake-id')
    assert resp.status_code == 404


# --- Activity ---

def test_activity_feed(auth_client):
    pid = _make_person(auth_client)
    _make_note(auth_client, pid, "Note 1", "meeting")
    _make_note(auth_client, pid, "Note 2", "call")

    resp = auth_client.get('/api/notes/activity')
    assert resp.status_code == 200
    activity = _data(resp)
    assert len(activity) >= 2
    assert all('person_name' in a for a in activity)


def test_activity_feed_limit(auth_client):
    pid = _make_person(auth_client)
    for i in range(5):
        _make_note(auth_client, pid, f"Note {i}")

    resp = auth_client.get('/api/notes/activity?limit=2')
    assert resp.status_code == 200
    assert len(_data(resp)) == 2


# --- Relationship scoring ---

def test_notes_update_relationship_score(auth_client):
    pid = _make_person(auth_client)
    _make_note(auth_client, pid, "First meeting", "meeting")
    _make_note(auth_client, pid, "Follow up call", "call")

    resp = auth_client.get(f'/api/people/{pid}')
    person = _data(resp)
    assert person['relationship_score'] > 0
    assert person['relationship_status'] == 'warm'
    assert person['interaction_count'] == 2
