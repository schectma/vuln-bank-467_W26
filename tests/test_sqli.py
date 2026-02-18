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


# testing forgot_password()
def test_forgot_password_vuln_inj(client, setup_test_db):
    """
    Tests if SQL injection allowed when vulnerable
    """
    toggle_harden(False)

    payload = {
        "username": "' OR '1'='1"
    }

    res = client.post("/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_password_vuln_correct(client, setup_test_db):
    """
    Tests if a valid username is accepted in vulnerable state.
    """
    toggle_harden(False)

    payload = {
        "username": "testuser1"
    }

    res = client.post("/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_password_vuln_incorrect(client, setup_test_db):
    """
    Tests if a non-existent username is rejected in vulnerable state.
    """
    toggle_harden(False)

    payload = {
        "username": "nonexistentuser"
    }

    res = client.post("/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"


def test_forgot_password_hardened_inj(client, setup_test_db):
    """
    Tests if SQL injection is blocked on forgot_password
    when in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "' OR '1'='1"
    }

    res = client.post("/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"


def test_forgot_password_hardened_correct(client, setup_test_db):
    """
    Tests if a valid username is accepted in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "testuser1"
    }

    res = client.post("/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_password_hardened_incorrect(client, setup_test_db):
    """
    Tests if a non-existent username is rejected in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "nonexistentuser"
    }

    res = client.post("/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"


# testing api_v1_forgot_password()
def test_forgot_v1_password_vuln_inj(client, setup_test_db):
    """
    Tests if SQL injection allowed when vulnerable
    """
    toggle_harden(False)

    payload = {
        "username": "' OR '1'='1"
    }

    res = client.post("/api/v1/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_v1_password_vuln_correct(client, setup_test_db):
    """
    Tests if a valid username is accepted in vulnerable state.
    """
    toggle_harden(False)

    payload = {
        "username": "testuser1"
    }

    res = client.post("/api/v1/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_v1_password_vuln_incorrect(client, setup_test_db):
    """
    Tests if a non-existent username is rejected in vulnerable state.
    """
    toggle_harden(False)

    payload = {
        "username": "nonexistentuser"
    }

    res = client.post("/api/v1/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"


def test_forgot_v1_password_hardened_inj(client, setup_test_db):
    """
    Tests if SQL injection is blocked on forgot_password
    when in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "' OR '1'='1"
    }

    res = client.post("/api/v1/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"


def test_forgot_v1_password_hardened_correct(client, setup_test_db):
    """
    Tests if a valid username is accepted in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "testuser1"
    }

    res = client.post("/api/v1/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_v1_password_hardened_incorrect(client, setup_test_db):
    """
    Tests if a non-existent username is rejected in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "nonexistentuser"
    }

    res = client.post("/api/v1/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"


# testing api_v2_forgot_password()
def test_forgot_v2_password_vuln_inj(client, setup_test_db):
    """
    Tests if SQL injection allowed when vulnerable
    """
    toggle_harden(False)

    payload = {
        "username": "' OR '1'='1"
    }

    res = client.post("/api/v2/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_v2_password_vuln_correct(client, setup_test_db):
    """
    Tests if a valid username is accepted in vulnerable state.
    """
    toggle_harden(False)

    payload = {
        "username": "testuser1"
    }

    res = client.post("/api/v2/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_v2_password_vuln_incorrect(client, setup_test_db):
    """
    Tests if a non-existent username is rejected in vulnerable state.
    """
    toggle_harden(False)

    payload = {
        "username": "nonexistentuser"
    }

    res = client.post("/api/v2/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"


def test_forgot_v2_password_hardened_inj(client, setup_test_db):
    """
    Tests if SQL injection is blocked on forgot_password
    when in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "' OR '1'='1"
    }

    res = client.post("/api/v2/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"


def test_forgot_v2_password_hardened_correct(client, setup_test_db):
    """
    Tests if a valid username is accepted in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "testuser1"
    }

    res = client.post("/api/v2/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_v2_password_hardened_incorrect(client, setup_test_db):
    """
    Tests if a non-existent username is rejected in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "nonexistentuser"
    }

    res = client.post("/api/v2/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"


# testing api_v3_forgot_password()
def test_forgot_v3_password_vuln_inj(client, setup_test_db):
    """
    Tests if SQL injection allowed when vulnerable
    """
    toggle_harden(False)

    payload = {
        "username": "' OR '1'='1"
    }

    res = client.post("/api/v3/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_v3_password_vuln_correct(client, setup_test_db):
    """
    Tests if a valid username is accepted in vulnerable state.
    """
    toggle_harden(False)

    payload = {
        "username": "testuser1"
    }

    res = client.post("/api/v3/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_v3_password_vuln_incorrect(client, setup_test_db):
    """
    Tests if a non-existent username is rejected in vulnerable state.
    """
    toggle_harden(False)

    payload = {
        "username": "nonexistentuser"
    }

    res = client.post("/api/v3/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"


def test_forgot_v3_password_hardened_inj(client, setup_test_db):
    """
    Tests if SQL injection is blocked on forgot_password
    when in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "' OR '1'='1"
    }

    res = client.post("/api/v3/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"


def test_forgot_v3_password_hardened_correct(client, setup_test_db):
    """
    Tests if a valid username is accepted in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "testuser1"
    }

    res = client.post("/api/v3/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"


def test_forgot_v3_password_hardened_incorrect(client, setup_test_db):
    """
    Tests if a non-existent username is rejected in hardened state.
    """
    toggle_harden(True)

    payload = {
        "username": "nonexistentuser"
    }

    res = client.post("/api/v3/forgot-password", json=payload)
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == "error"
