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


# testing create_admin()
def test_create_admin_vuln_inj(admin_client, user_exists):
    """
    Tests if SQL injection allowed when in vulnerable state
    Logs in as admin using admin_client
    """
    payload = {
        "username": (
            "newuser1', 'foo', '1540', true); DELETE FROM users "
            "WHERE username = 'testuser1';--"
        ),
        "password": "password"
    }

    res = admin_client.post("/admin/create_admin", json=payload)
    assert res.status_code == 200

    # testuser1 should have been deleted
    assert user_exists("testuser1") is False


def test_create_admin_hardened_inj(hardened_admin_client, user_exists):
    """
    Tests if SQL injection allowed when in hardened state
    Logs in as admin using hardened_admin_client
    """

    payload = {
        "username": (
            "newuser1', 'foo', '1540', true); DELETE FROM users "
            "WHERE username = 'testuser1';--"
        ),
        "password": "password"
    }

    res = hardened_admin_client.post("/admin/create_admin", json=payload)
    assert res.status_code == 200

    # testuser1 should still exist
    assert user_exists("testuser1") is True


def test_create_admin_vuln_correct(admin_client, user_exists):
    """
    Tests if can create admin with correct info in vulnerable mode
    """

    payload = {
        "username": "newuser",
        "password": "password"
    }

    res = admin_client.post("/admin/create_admin", json=payload)
    assert res.status_code == 200

    assert user_exists("newuser") is True


def test_create_admin_hardened_correct(hardened_admin_client, user_exists):
    """
    Tests if can create admin with correct info in hardened mode
    """

    payload = {
        "username": "newuser",
        "password": "password"
    }

    res = hardened_admin_client.post("/admin/create_admin", json=payload)
    assert res.status_code == 200

    assert user_exists("newuser") is True


def test_create_admin_vuln_incorrect(admin_client, user_exists):
    """
    Tests if can create admin with incorrect info in vulnerable mode
    This is trying to create an admin that already exists
    """

    payload = {
        "username": "admin",
        "password": "password"
    }

    res = admin_client.post("/admin/create_admin", json=payload)
    assert res.status_code == 500


def test_create_admin_hardened_incorrect(hardened_admin_client, user_exists):
    """
    Tests if can create admin with incorrect info in hardened mode
    This is trying to create an admin that already exists
    """

    payload = {
        "username": "admin",
        "password": "password"
    }

    res = hardened_admin_client.post("/admin/create_admin", json=payload)
    assert res.status_code == 500


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


def test_api_transactions_hardened_inj(
    hardened_user_client,
    setup_transactions_db
):
    """
    Tests that transactions are not returned when injection used
    in hardened mode
    """

    injection = "' OR '1'='1"

    res = hardened_user_client.get(
        f"/api/transactions?account_number={injection}"
    )
    data = res.get_json()

    assert res.status_code == 200
    # Parameterized query treats the payload as a literal — no matches
    assert data["transactions"] == []


def test_api_transactions_hardened_valid(
    hardened_user_client,
    setup_transactions_db
):
    """
    Tests that transactions are returned for a valid account number
    """
    res = hardened_user_client.get(
        "/api/transactions?account_number=TEST001"
    )
    data = res.get_json()

    assert res.status_code == 200
    assert data["account_number"] == "TEST001"
    assert len(data["transactions"]) > 0


def test_api_transactions_hardened_invalid(
    hardened_user_client,
    setup_transactions_db
):
    """
    Tests that an empty list is returned for invalid account numbers
    """
    res = hardened_user_client.get(
        "/api/transactions?account_number=DOESNOTEXIST"
    )
    data = res.get_json()

    assert res.status_code == 200
    assert data["transactions"] == []


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
