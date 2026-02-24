from helper import toggle_harden

def test_update_card_limit_ma_hardened(client, setup_test_db):
    """Verify that only allowed fields can be updated when MA mitigation is enabled."""
    toggle_harden(True)

    # Attacker logs in as testuser2
    payload = {"username": "testuser2", "password": "testpassword2"}
    res = client.post("/login", json=payload)
    assert res.status_code == 200
    token = res.get_json()["token"]

    # Attacker tries to update card with a disallowed field
    victim_card_id = 1  # Assuming testuser1's card has id=1 in test DB
    headers = {"Authorization": f"Bearer {token}"}
    update_payload = {
        "card_limit": 5000,
        "current_balance": 9999.99,  # Not allowed in hardened mode
        "is_frozen": True            # Not allowed in hardened mode
    }
    res = client.post(
        f"/api/virtual-cards/{victim_card_id}/update-limit",
        json=update_payload,
        headers=headers
    )
    data = res.get_json()

    # Should be forbidden or error
    assert res.status_code == 400 or res.status_code == 403
    assert data["status"] == "error"
    assert (
        "invalid field" in data["message"].lower()
        or "not authorized" in data["message"].lower()
        or "access denied" in data["message"].lower()
        or "illegal payload" in data["message"].lower()
    )
