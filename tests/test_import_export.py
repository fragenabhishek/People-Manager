"""Tests for CSV/JSON import and export."""
import csv
import io
import json

from conftest import _data, _json


def _create_person(client, name="Export Person"):
    return client.post('/api/people',
                       data=json.dumps({"name": name, "company": "TestCo"}),
                       content_type='application/json')


# --- Import ---

def test_csv_import(auth_client):
    csv_content = "name,email,company\nAlice,a@b.com,Co1\nBob,b@c.com,Co2\n"
    data = {'file': (io.BytesIO(csv_content.encode()), 'contacts.csv')}
    resp = auth_client.post('/api/people/import/csv', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    result = _data(resp)
    assert result['imported'] == 2
    assert result['skipped'] == 0


def test_csv_import_no_file(auth_client):
    resp = auth_client.post('/api/people/import/csv')
    assert resp.status_code == 400


def test_csv_import_wrong_format(auth_client):
    data = {'file': (io.BytesIO(b'not csv'), 'data.txt')}
    resp = auth_client.post('/api/people/import/csv', data=data, content_type='multipart/form-data')
    assert resp.status_code == 400


# --- CSV Export ---

def test_csv_export(auth_client):
    _create_person(auth_client, "Alice")
    _create_person(auth_client, "Bob")

    resp = auth_client.get('/api/people/export/csv')
    assert resp.status_code == 200
    assert 'text/csv' in resp.content_type
    assert 'contacts.csv' in resp.headers.get('Content-Disposition', '')

    reader = csv.DictReader(io.StringIO(resp.data.decode()))
    rows = list(reader)
    assert len(rows) == 2
    assert 'name' in reader.fieldnames


# --- JSON Export ---

def test_json_export(auth_client):
    _create_person(auth_client, "Alice")
    _create_person(auth_client, "Bob")

    resp = auth_client.get('/api/people/export/json')
    assert resp.status_code == 200
    assert 'application/json' in resp.content_type

    data = json.loads(resp.data)
    assert len(data) == 2
    assert all('user_id' not in d for d in data)
