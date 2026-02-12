from helper import toggle_harden


# testing login()
def test_login_vuln_inj(client, setup_test_db):
    """
    Tests if SQL injection allowed when in vulnerable state
    """
    toggle_harden(False)

    payload = {
        "username": "admin' --",
        "password": "irrelevant"
    }

    res = client.post("/login", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_login_vuln_correct(client, setup_test_db):
    """
    Tests if correct login allowed in vulnerable state
    """
    toggle_harden(False)

    payload = {
        "username": "admin",
        "password": "admin123"
    }

    res = client.post("/login", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_login_vuln_incorrect(client, setup_test_db):
    """
    Tests if incorrect login allowed in vulnerable state
    """
    toggle_harden(False)

    payload = {
        "username": "adn",
        "password": "adn123"
    }

    res = client.post("/login", json=payload)
    data = res.get_json()

    assert res.status_code == 401
    assert data["status"] == "error"


def test_login_hardened_inj(client, setup_test_db):
    """
    Tests if SQL injection allowed when in hardened state
    """
    toggle_harden(True)

    payload = {
        "username": "admin' --",
        "password": "irrelevant"
    }

    res = client.post("/login", json=payload)
    data = res.get_json()

    assert res.status_code == 401
    assert data["status"] == "error"


def test_login_hardened_correct(client, setup_test_db):
    """
    Tests if correct login allowed in hardened state
    """
    toggle_harden(True)

    payload = {
        "username": "testuser1",
        "password": "testpassword1"
    }

    res = client.post("/login", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"
    assert "token" in data


def test_login_hardened_incorrect(client, setup_test_db):
    """
    Tests if incorrect login allowed in hardened state
    """
    toggle_harden(True)

    payload = {
        "username": "adn",
        "password": "adn123"
    }

    res = client.post("/login", json=payload)
    data = res.get_json()

    assert res.status_code == 401
    assert data["status"] == "error"
