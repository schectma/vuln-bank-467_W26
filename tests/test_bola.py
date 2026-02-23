from helper import toggle_harden


def test_check_balance_bola_hardened(client, setup_test_db):
    """Verify that attempt to check balance of another user fails."""
    toggle_harden(True)

    # Attacker logs in as testuser2
    payload = {"username": "testuser2", "password": "testpassword2"}
    res = client.post("/login", json=payload)
    assert res.status_code == 200
    token = res.get_json()["token"]

    # Attacker tries to access testuser1's account
    victim_account_number = "TEST001"
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get(f"/check_balance/{victim_account_number}", headers=headers)
    data = res.get_json()

    # Should be forbidden or error
    assert res.status_code == 403
    assert data["status"] == "error"
    assert "Account not found" in data["message"] or "access denied" in data["message"]


def test_get_transaction_history_bola_hardened(client, setup_test_db):
    """Verify that attempt to view another user's transaction history fails."""
    toggle_harden(True)

    # Attacker logs in as testuser2
    payload = {"username": "testuser2", "password": "testpassword2"}
    res = client.post("/login", json=payload)
    assert res.status_code == 200
    token = res.get_json()["token"]

    # Attacker tries to access testuser1's transaction history
    victim_account_number = "TEST001"
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get(f"/transactions/{victim_account_number}", headers=headers)
    data = res.get_json()

    # Should be forbidden or error
    assert res.status_code == 403
    assert data["status"] == "error"
    assert (
        "not authorized" in data["message"].lower()
        or "access denied" in data["message"].lower()
        or "not found" in data["message"].lower()
    )


def test_toggle_card_freeze_bola_hardened(client, setup_test_db):
    """Verify that attempt to freeze/unfreeze another user's card fails."""
    toggle_harden(True)

    # Attacker logs in as testuser2
    payload = {"username": "testuser2", "password": "testpassword2"}
    res = client.post("/login", json=payload)
    assert res.status_code == 200
    token = res.get_json()["token"]

    # Attacker tries to freeze/unfreeze testuser1's card
    victim_card_id = 1  # Assuming testuser1's card has id=1 in test DB
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(f"/api/virtual-cards/{victim_card_id}/toggle-freeze", headers=headers)
    data = res.get_json()

    # Should be forbidden or error
    assert res.status_code == 403
    assert data["status"] == "error"
    assert (
        "not authorized" in data["message"].lower()
        or "access denied" in data["message"].lower()
        or "not found" in data["message"].lower()
    )


def test_get_card_transactions_bola_hardened(client, setup_test_db):
    """Verify that attempt to view another user's card transactions fails."""
    toggle_harden(True)

    # Attacker logs in as testuser2
    payload = {"username": "testuser2", "password": "testpassword2"}
    res = client.post("/login", json=payload)
    assert res.status_code == 200
    token = res.get_json()["token"]

    # Attacker tries to access testuser1's card transactions
    victim_card_id = 1  # Assuming testuser1's card has id=1 in test DB
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get(f"/api/virtual-cards/{victim_card_id}/transactions", headers=headers)
    data = res.get_json()

    # Should be forbidden or error
    assert res.status_code == 403
    assert data["status"] == "error"
    assert (
        "not authorized" in data["message"].lower()
        or "access denied" in data["message"].lower()
        or "not found" in data["message"].lower()
    )


def test_update_card_limit_bola_hardened(client, setup_test_db):
    """Verify that attempt to update another user's card limit fails."""
    toggle_harden(True)

    # Attacker logs in as testuser2
    payload = {"username": "testuser2", "password": "testpassword2"}
    res = client.post("/login", json=payload)
    assert res.status_code == 200
    token = res.get_json()["token"]

    # Attacker tries to update testuser1's card limit
    victim_card_id = 1  # Assuming testuser1's card has id=1 in test DB
    headers = {"Authorization": f"Bearer {token}"}
    update_payload = {"card_limit": 5000}
    res = client.post(
        f"/api/virtual-cards/{victim_card_id}/update-limit",
        json=update_payload,
        headers=headers
    )
    data = res.get_json()

    # Should be forbidden or error
    assert res.status_code == 403
    assert data["status"] == "error"
    assert (
        "not authorized" in data["message"].lower()
        or "access denied" in data["message"].lower()
        or "not found" in data["message"].lower()
        or "illegal payload" in data["message"].lower()
    )
