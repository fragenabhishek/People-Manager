"""
Integration tests that run the full Flask app with SQLite as the database.
Proves that all API endpoints work identically with the SQL backend.
"""
import json
import os

import pytest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ.setdefault('FLASK_DEBUG', 'True')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-pytest-32chars!')

from app import create_app
from conftest import _data, _json


@pytest.fixture()
def sql_app():
    from config import Config
    orig_sql = Config.USE_SQL
    orig_db_url = Config.DATABASE_URL
    orig_mongo = Config.USE_MONGODB

    Config.DATABASE_URL = 'sqlite:///:memory:'
    Config.USE_SQL = True
    Config.USE_MONGODB = False

    application = create_app()
    application.config['TESTING'] = True

    yield application

    Config.USE_SQL = orig_sql
    Config.DATABASE_URL = orig_db_url
    Config.USE_MONGODB = orig_mongo


@pytest.fixture()
def sql_client(sql_app):
    return sql_app.test_client()


@pytest.fixture()
def sql_auth_client(sql_client):
    sql_client.post('/register', data={
        'username': 'sqluser',
        'password': 'password123',
        'confirm_password': 'password123',
    })
    sql_client.post('/login', data={
        'username': 'sqluser',
        'password': 'password123',
    })
    return sql_client


def test_health_reports_postgresql(sql_client):
    resp = sql_client.get('/health')
    data = resp.get_json()
    assert data['storage'] == 'postgresql'


def test_register_login_flow(sql_client):
    resp = sql_client.post('/register', data={
        'username': 'newuser',
        'password': 'pass123',
        'confirm_password': 'pass123',
    })
    assert resp.status_code == 302

    resp = sql_client.post('/login', data={
        'username': 'newuser',
        'password': 'pass123',
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_crud_people(sql_auth_client):
    resp = sql_auth_client.post('/api/people',
                                data=json.dumps({'name': 'SQL Contact', 'company': 'TestCo'}),
                                content_type='application/json')
    assert resp.status_code == 201
    person = _data(resp)
    person_id = person['id']

    resp = sql_auth_client.get('/api/people')
    assert resp.status_code == 200
    people = _data(resp)
    assert len(people) == 1
    assert people[0]['name'] == 'SQL Contact'

    resp = sql_auth_client.get(f'/api/people/{person_id}')
    assert resp.status_code == 200

    resp = sql_auth_client.put(f'/api/people/{person_id}',
                               data=json.dumps({'name': 'Updated', 'company': 'NewCo'}),
                               content_type='application/json')
    assert resp.status_code == 200
    assert _data(resp)['company'] == 'NewCo'

    resp = sql_auth_client.delete(f'/api/people/{person_id}')
    assert resp.status_code == 200


def test_notes_crud(sql_auth_client):
    resp = sql_auth_client.post('/api/people',
                                data=json.dumps({'name': 'Note Target'}),
                                content_type='application/json')
    person_id = _data(resp)['id']

    resp = sql_auth_client.post(f'/api/notes/person/{person_id}',
                                data=json.dumps({'content': 'Hello from SQL', 'note_type': 'meeting'}),
                                content_type='application/json')
    assert resp.status_code == 201
    note_id = _data(resp)['id']

    resp = sql_auth_client.get(f'/api/notes/person/{person_id}')
    assert resp.status_code == 200
    assert len(_data(resp)) == 1

    resp = sql_auth_client.delete(f'/api/notes/{note_id}')
    assert resp.status_code == 200


def test_search(sql_auth_client):
    sql_auth_client.post('/api/people',
                         data=json.dumps({'name': 'Alice Wonderland', 'company': 'MagicCorp'}),
                         content_type='application/json')
    sql_auth_client.post('/api/people',
                         data=json.dumps({'name': 'Bob Builder'}),
                         content_type='application/json')

    resp = sql_auth_client.get('/api/people/search/alice')
    assert resp.status_code == 200
    assert len(_data(resp)) == 1


def test_tags(sql_auth_client):
    resp = sql_auth_client.post('/api/people',
                                data=json.dumps({'name': 'Tagged', 'tags': ['vip', 'friend']}),
                                content_type='application/json')

    resp = sql_auth_client.get('/api/people/tags')
    tags = _data(resp)
    assert 'vip' in tags
    assert 'friend' in tags

    resp = sql_auth_client.get('/api/people?tag=vip')
    assert len(_data(resp)) == 1


def test_dashboard_stats(sql_auth_client):
    sql_auth_client.post('/api/people',
                         data=json.dumps({'name': 'D1'}),
                         content_type='application/json')
    resp = sql_auth_client.get('/api/people/dashboard/stats')
    assert resp.status_code == 200
    stats = _data(resp)
    assert stats['total_contacts'] == 1


def test_jwt_with_sql_backend(sql_client):
    resp = sql_client.post('/api/auth/register',
                           data=json.dumps({
                               'username': 'jwtuser',
                               'password': 'secret123',
                               'confirm_password': 'secret123',
                           }),
                           content_type='application/json')
    assert resp.status_code == 201
    token = _data(resp)['access_token']

    resp = sql_client.get('/api/auth/me',
                          headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert _data(resp)['username'] == 'jwtuser'
