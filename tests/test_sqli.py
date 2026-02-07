import pytest
import json
from app import app
import app as app_module   # Import whole module so we can toggle harden


@pytest.fixture
def client():
    # Puts Flask into testing mode
    app.config["TESTING"] = True
    # Creates Flask test client
    with app.test_client() as client:
        yield client

def toggle_harden(state: bool):
    """
    Helper function to toggle hardening on/off.
    """
    app_module.harden = state
    app.config["HARDENED"] = state

# testing login()
def login_vuln(client):
toggle_harden(False)

    payload = {
        "username": "admin' --",
        "password": "irrelevant"
    }

    res = client.post("/login", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success", "SQL injection should succeed in unhardened mode"

def login_hardened(client):
    toggle_harden(True)

    payload = {
        "username": "testuser",
        "password": "password123"
    }

    res = client.post("/login", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"
    assert "token" in data
