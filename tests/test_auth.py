import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.testing = True
    with flask_app.test_client() as client:
        yield client

# Helper to get logged_in value

def get_user_id_from_session(client):
    with client.session_transaction() as sess:
        return sess.get('user_id')

# Use the seeded user from seed_db: demo@spendly.com with password demo123

def test_login_get(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"Login" in resp.data

def test_login_success(client):
    resp = client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"}, follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith("/profile")
    # session should contain user_id
    assert get_user_id_from_session(client) is not None

def test_login_failure_wrong_password(client):
    resp = client.post("/login", data={"email": "demo@spendly.com", "password": "wrong"})
    assert resp.status_code == 401

def test_login_failure_missing_fields(client):
    resp = client.post("/login", data={"email": "demo@spendly.com"})
    assert resp.status_code == 400

def test_logout_not_logged_in(client):
    resp = client.get("/logout")
    assert resp.status_code == 401

def test_logout_success(client):
    # First log in
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    # Then logout
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith("/login")
    # session cleared
    assert get_user_id_from_session(client) is None

