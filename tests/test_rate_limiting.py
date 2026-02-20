from helper import toggle_harden


# Login Tests

def test_login_not_rate_limited_when_vulnerable(client, setup_test_db):
    """
    Tests that rate limiting is ignored in vulnerable mode.
    """
    toggle_harden(False)

    payload = {
        "username": "testuser1",
        "password": "wrongpass"
    }

    for _ in range(8):
        res = client.post("/login", json=payload)
        assert res.status_code != 429


def test_login_rate_limited_when_hardened(client, setup_test_db):
    """
    Tests that rate limiting is enforced when hardened.
    """
    toggle_harden(True)

    payload = {
        "username": "testuser1",
        "password": "wrongpass"
    }

    for _ in range(6):
        res = client.post("/login", json=payload)
        assert res.status_code != 429

    res = client.post("/login", json=payload)
    assert res.status_code == 429

    data = res.get_json()
    assert data["status"] == "error"
    assert "Too many requests" in data["message"]


# Reset Password Tests

def test_reset_pw_not_rate_limited_when_vulnerable(client, setup_test_db):
    """
    Tests that rate limiting is ignored in vulnerable mode.
    """
    toggle_harden(False)

    payload = {
        "username": "testuser1",
        "reset_pin": "0000",
        "new_password": "newpass1"
    }

    for _ in range(7):
        res = client.post("/reset-password", json=payload)
        assert res.status_code != 429


def test_reset_pw_rate_limited_when_hardened(client, setup_test_db):
    """
    Tests that rate limiting is enforced when hardened.
    """
    toggle_harden(True)

    payload = {
        "username": "testuser1",
        "reset_pin": "0000",
        "new_password": "newpass1"
    }

    for _ in range(5):
        res = client.post("/reset-password", json=payload)
        assert res.status_code != 429

    res = client.post("/reset-password", json=payload)
    assert res.status_code == 429

    data = res.get_json()
    assert data["status"] == "error"
    assert "Too many requests" in data["message"]
