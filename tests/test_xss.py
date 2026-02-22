from helper import toggle_harden


XSS_PAYLOAD = '<img src=x onerror="alert(\'XSS\')">'


def test_transfer_xss_vuln(user_client, setup_transactions_db):
    """
    Tests that XSS payload is stored unsanitized in vulnerable mode.
    """
    toggle_harden(False)

    res = user_client.post("/transfer", json={
        "to_account": "TEST002",
        "amount": 10,
        "description": XSS_PAYLOAD
    })
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"

    # Retrieve transaction history and verify payload is stored raw
    res = user_client.get("/transactions/TEST001")
    data = res.get_json()

    descriptions = [t["description"] for t in data["transactions"]]
    assert XSS_PAYLOAD in descriptions


def test_transfer_xss_hardened(hardened_user_client, setup_transactions_db):
    """
    Tests that XSS payload is stored in hardened mode and the response
    includes the X-XSS-Protection security header.
    """
    res = hardened_user_client.post("/transfer", json={
        "to_account": "TEST002",
        "amount": 10,
        "description": XSS_PAYLOAD
    })
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"

    # Verify the response includes the X-XSS-Protection header
    res = hardened_user_client.get("/transactions/TEST001")
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"


def test_bill_payment_xss_vuln(user_client, setup_bill_payments_db):
    """
    Tests that XSS payload is stored unsanitized in bill payment description.
    """
    toggle_harden(False)

    res = user_client.post("/api/bill-payments/create", json={
        "biller_id": 1,
        "amount": 50,
        "payment_method": "balance",
        "description": XSS_PAYLOAD
    })
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"

    # Retrieve payment history and verify payload is stored raw
    res = user_client.get("/api/bill-payments/history")
    data = res.get_json()

    descriptions = [p["description"] for p in data["payments"]]
    assert XSS_PAYLOAD in descriptions


def test_bill_payment_xss_hardened(hardened_user_client, setup_bill_payments_db):
    """
    Tests that XSS payload is stored in hardened mode and the response
    includes the X-XSS-Protection security header.
    """
    res = hardened_user_client.post("/api/bill-payments/create", json={
        "biller_id": 1,
        "amount": 50,
        "payment_method": "balance",
        "description": XSS_PAYLOAD
    })
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"

    # Verify the response includes the X-XSS-Protection header
    res = hardened_user_client.get("/api/bill-payments/history")
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
