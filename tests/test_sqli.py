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

# tests api_transactions()
def test_api_transactions_vuln_inj(user_client, setup_transactions_db):
    """
    Tests if SQL injection allowed in vulnerable mode
    """
    injection = "' OR '1'='1"

    res = user_client.get(f"/api/transactions?account_number={injection}")
    data = res.get_json()

    assert res.status_code == 200
    # Injection causes all transactions to be returned, not just TEST001's
    assert len(data["transactions"]) > 1

def test_api_transactions_vuln_valid(user_client, setup_transactions_db):
    """
    Tests that transactions are returned for a valid account number
    """
    res = user_client.get("/api/transactions?account_number=TEST001")
    data = res.get_json()

    assert res.status_code == 200
    assert data["account_number"] == "TEST001"
    assert len(data["transactions"]) > 0

def test_api_transactions_vuln_invalid(user_client, setup_transactions_db):
    """
    Tests that transactions are not returned for invalid account number
    """
    res = user_client.get("/api/transactions?account_number=DOESNOTEXIST")
    data = res.get_json()

    assert res.status_code == 200
    assert data["transactions"] == []

def test_api_transactions_hardened_inj(hardened_user_client, setup_transactions_db):
    """
    Tests that transactions are not returned when injection used
    in hardened mode
    """

    injection = "' OR '1'='1"

    res = hardened_user_client.get(f"/api/transactions?account_number={injection}")
    data = res.get_json()

    assert res.status_code == 200
    # Parameterized query treats the payload as a literal — no matches
    assert data["transactions"] == []

def test_api_transactions_hardened_valid(hardened_user_client, setup_transactions_db):
    """
    Tests that transactions are returned for a valid account number
    """
    res = hardened_user_client.get("/api/transactions?account_number=TEST001")
    data = res.get_json()

    assert res.status_code == 200
    assert data["account_number"] == "TEST001"
    assert len(data["transactions"]) > 0

def test_api_transactions_hardened_invalid(hardened_user_client, setup_transactions_db):
    """
    Tests that an empty list is returned for invalid account numbers
    """
    res = hardened_user_client.get("/api/transactions?account_number=DOESNOTEXIST")
    data = res.get_json()

    assert res.status_code == 200
    assert data["transactions"] == []
