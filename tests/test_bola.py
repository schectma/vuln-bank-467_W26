import mitigations.BOLA as BOLA
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