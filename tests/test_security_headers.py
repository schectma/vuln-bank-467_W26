from helper import toggle_harden


SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
}


def test_security_headers_missing_when_vulnerable(user_client):
    """
    Tests that security headers are absent in vulnerable mode.
    """
    toggle_harden(False)

    res = user_client.get("/dashboard")

    for header in SECURITY_HEADERS:
        assert res.headers.get(header) is None, (
            f"Header '{header}' should be absent in vulnerable mode"
        )


def test_security_headers_vuln_correct(user_client):
    """
    Tests that the dashboard still returns 200 in vulnerable mode
    even without security headers.
    """
    toggle_harden(False)

    res = user_client.get("/dashboard")

    assert res.status_code == 200


def test_security_headers_present_when_hardened(hardened_user_client):
    """
    Tests that all security headers are present with correct values
    in hardened mode.
    """
    res = hardened_user_client.get("/dashboard")

    for header, expected_value in SECURITY_HEADERS.items():
        actual = res.headers.get(header)
        assert actual == expected_value, (
            f"Header '{header}' expected '{expected_value}', got '{actual}'"
        )


def test_security_headers_hardened_correct(hardened_user_client):
    """
    Tests that the dashboard still returns 200 in hardened mode
    with security headers present.
    """
    res = hardened_user_client.get("/dashboard")

    assert res.status_code == 200
