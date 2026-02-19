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


# testing create_virtual_card()
def test_create_virtual_card_vuln_inj(
    user_client,
    setup_test_db,
    setup_virtual_cards_db
):
    """
    Tests if SQL injection for card_type possible in vulnerable mode
    """
    toggle_harden(False)

    # Return id is commented out so returns None
    payload = {
        "card_limit": 500.0,
        "card_type": "anything'); --"
    }

    res = user_client.post("/api/virtual-cards/create", json=payload)
    data = res.get_json()

    # The injection causes the query to fail (transaction is rolled back),
    # so no card row is persisted. The endpoint returns 500.
    assert res.status_code == 500
    assert data["status"] == "error"


def test_create_virtual_card_vuln_correct(
    user_client,
    setup_test_db,
    setup_virtual_cards_db
):
    """
    Tests that a virtual card is created with valid input in vulnerable mode.
    """
    toggle_harden(False)

    payload = {
        "card_limit": 500.0,
        "card_type": "standard"
    }

    res = user_client.post("/api/virtual-cards/create", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"
    # Checks card details from the endpoint
    # This card is successfully added to the database
    assert data["card_details"]["limit"] == 500.0
    assert data["card_details"]["type"] == "standard"


def test_create_virtual_card_vuln_incorrect(
    user_client,
    setup_test_db,
    setup_virtual_cards_db
):
    """
    Tests behavior with invalid input in vulnerable mode.
    card_limit is cast to float, so a non-numeric value causes an error.
    """
    toggle_harden(False)

    payload = {
        "card_limit": "not_a_number",
        "card_type": "standard"
    }

    res = user_client.post("/api/virtual-cards/create", json=payload)
    data = res.get_json()

    assert res.status_code == 500
    assert data["status"] == "error"


def test_create_virtual_card_hardened_inj(
    hardened_user_client,
    setup_test_db,
    setup_virtual_cards_db
):
    """
    Tests that SQL injection via card_type is blocked in hardened mode.
    The parameterized query treats the payload as a literal string,
    so the card is created with the injection string as the card_type value.
    Users being able to create their own cards is a separate vulnerability.
    """
    payload = {
        "card_limit": 500.0,
        "card_type": "anything'); --"
    }

    res = hardened_user_client.post("/api/virtual-cards/create", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"
    assert data["card_details"]["type"] == "anything'); --"


def test_create_virtual_card_hardened_correct(
    hardened_user_client,
    setup_test_db,
    setup_virtual_cards_db
):
    """
    Tests that a virtual card is created with valid input in hardened mode.
    """
    payload = {
        "card_limit": 500.0,
        "card_type": "standard"
    }

    res = hardened_user_client.post("/api/virtual-cards/create", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"
    assert data["card_details"]["limit"] == 500.0
    assert data["card_details"]["type"] == "standard"


def test_create_virtual_card_hardened_incorrect(
    hardened_user_client,
    setup_test_db,
    setup_virtual_cards_db
):
    """
    Tests that user cannot create card in hardened mode
    with incorrect information.
    """
    payload = {
        "card_limit": "not_a_number",
        "card_type": "standard"
    }

    res = hardened_user_client.post("/api/virtual-cards/create", json=payload)
    data = res.get_json()

    assert res.status_code == 500
    assert data["status"] == "error"
