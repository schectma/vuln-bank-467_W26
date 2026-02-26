from helper import toggle_harden


# ──────────────────────────────────────────────
# Debug Mode in Production
# ──────────────────────────────────────────────


def test_debug_endpoint_exposes_users_when_vulnerable(user_client):
    """
    Tests that /debug/users returns sensitive user data
    in vulnerable mode.
    """
    toggle_harden(False)

    res = user_client.get("/debug/users")
    data = res.get_json()

    assert res.status_code == 200
    assert "users" in data
    assert len(data["users"]) > 0

    # Verify sensitive fields are exposed
    user = data["users"][0]
    assert "password" in user
    assert "account_number" in user
    assert "is_admin" in user


def test_debug_endpoint_correct_data_when_vulnerable(user_client):
    """
    Tests that /debug/users returns properly structured user
    records in vulnerable mode (correct behavior).
    """
    toggle_harden(False)

    res = user_client.get("/debug/users")
    data = res.get_json()

    assert res.status_code == 200

    user = data["users"][0]
    assert "id" in user
    assert "username" in user
    assert isinstance(user["username"], str)
    assert isinstance(user["is_admin"], bool)


def test_debug_endpoint_blocked_when_hardened(hardened_user_client):
    """
    Tests that /debug/users returns 404 in hardened mode.
    """
    res = hardened_user_client.get("/debug/users")
    data = res.get_json()

    assert res.status_code == 404
    assert data["message"] == "Not found"


def test_error_response_verbose_when_vulnerable(user_client, setup_bill_payments_db):
    """
    Tests that error responses include detailed debug info
    (error_type, timestamp) in vulnerable mode.
    """
    toggle_harden(False)

    res = user_client.post("/api/bill-payments/create", json={
        "biller_id": 999999,
        "amount": -100,
        "payment_method": "balance",
        "description": "trigger error",
    })

    data = res.get_json()
    assert res.status_code == 500
    assert "error_type" in data or "message" in data

    # In vulnerable mode the raw error string should appear
    # rather than a generic "contact support" message
    msg = data.get("message", "")
    assert "contact support" not in msg.lower()


def test_error_response_generic_when_hardened(
    hardened_user_client, setup_bill_payments_db
):
    """
    Tests that error responses hide internals and show a generic
    message in hardened mode.
    """
    res = hardened_user_client.post("/api/bill-payments/create", json={
        "biller_id": 999999,
        "amount": -100,
        "payment_method": "balance",
        "description": "trigger error",
    })

    data = res.get_json()
    assert res.status_code == 500

    # Should NOT leak error_type or debug_info
    assert "error_type" not in data
    assert "debug_info" not in data


def test_valid_bill_payment_works_when_vulnerable(
    user_client, setup_bill_payments_db
):
    """
    Tests that a valid bill payment succeeds in vulnerable mode
    (correct behavior).
    """
    toggle_harden(False)

    res = user_client.post("/api/bill-payments/create", json={
        "biller_id": 1,
        "amount": 50.00,
        "payment_method": "balance",
        "description": "Electric bill",
    })

    assert res.status_code in (200, 201)


def test_valid_bill_payment_works_when_hardened(
    hardened_user_client, setup_bill_payments_db
):
    """
    Tests that a valid bill payment succeeds in hardened mode
    (correct behavior).
    """
    res = hardened_user_client.post("/api/bill-payments/create", json={
        "biller_id": 1,
        "amount": 50.00,
        "payment_method": "balance",
        "description": "Electric bill",
    })

    assert res.status_code in (200, 201)


def test_normal_endpoint_works_when_hardened(hardened_user_client):
    """
    Tests that normal endpoints (dashboard) still work
    in hardened mode even though debug is disabled.
    """
    res = hardened_user_client.get("/dashboard")

    assert res.status_code == 200
