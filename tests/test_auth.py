"""Tests for authentication (register, login, logout)."""


def test_register_success(client):
    resp = client.post("/register", data={
        "username": "newuser",
        "password": "secret123",
        "confirm_password": "secret123",
    }, follow_redirects=False)
    assert resp.status_code == 303
    assert "/login" in resp.headers["location"]


def test_register_empty_username(client):
    resp = client.post("/register", data={
        "username": "",
        "password": "secret123",
        "confirm_password": "secret123",
    })
    assert resp.status_code == 200
    text = resp.text.lower()
    assert "required" in text or "error" in text


def test_register_short_password(client):
    resp = client.post("/register", data={
        "username": "newuser",
        "password": "123",
        "confirm_password": "123",
    })
    assert resp.status_code == 200
    text = resp.text.lower()
    assert "at least" in text or "character" in text


def test_register_password_mismatch(client):
    resp = client.post("/register", data={
        "username": "newuser",
        "password": "secret123",
        "confirm_password": "different",
    })
    assert resp.status_code == 200
    assert "match" in resp.text.lower()


def test_register_duplicate_username(client):
    client.post("/register", data={
        "username": "dupuser",
        "password": "secret123",
        "confirm_password": "secret123",
    })
    resp = client.post("/register", data={
        "username": "dupuser",
        "password": "secret123",
        "confirm_password": "secret123",
    })
    assert resp.status_code == 200
    assert "exists" in resp.text.lower()


def test_login_success(client):
    client.post("/register", data={
        "username": "loginuser",
        "password": "secret123",
        "confirm_password": "secret123",
    })
    resp = client.post("/login", data={
        "username": "loginuser",
        "password": "secret123",
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_login_wrong_password(client):
    client.post("/register", data={
        "username": "loginuser2",
        "password": "secret123",
        "confirm_password": "secret123",
    })
    resp = client.post("/login", data={
        "username": "loginuser2",
        "password": "wrongpassword",
    })
    assert "invalid" in resp.text.lower()


def test_logout(auth_client):
    resp = auth_client.get("/logout", follow_redirects=False)
    assert resp.status_code == 303

    resp = auth_client.get("/api/people")
    assert resp.status_code == 401
