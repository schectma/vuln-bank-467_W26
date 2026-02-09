from helper import toggle_harden

# See the conftest.py file in /tests
# It sets up a testing database separately from the development database.
# These tests are assuming that the vulnerability toggle is set to off.


def test_login_valid(client, setup_test_db):
    """
    Tests that the user 'testuser1' is able to log into
    the app with the correct username and password.
    """
    toggle_harden(False)

    payload = {
        "username": "testuser1",
        "password": "testpassword1"
    }

    res = client.post("/login", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"
    assert "token" in data


def test_login_invalid(client, setup_test_db):
    """
    Tests that the user 'testuser1' is not able to log into
    the app with the correct username and password.
    """
    toggle_harden(False)

    payload = {
        "username": "testuser1",
        "password": "123"
    }

    res = client.post("/login", json=payload)
    data = res.get_json()

    assert res.status_code == 401
    assert data["status"] == "error"
    assert "token" in data
