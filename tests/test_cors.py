from helper import toggle_harden


# ──────────────────────────────────────────────
# Permissive CORS Policy
# ──────────────────────────────────────────────

CROSS_ORIGIN = "http://evil.com"
SAME_ORIGIN = "http://localhost"


def test_cors_allows_any_origin_when_vulnerable(user_client):
    """
    Tests that the server echoes back any Origin and sets
    Access-Control-Allow-Origin to that origin in vulnerable mode.
    """
    toggle_harden(False)

    res = user_client.get(
        "/api/security-config",
        headers={"Origin": CROSS_ORIGIN},
    )

    assert res.headers.get("Access-Control-Allow-Origin") == CROSS_ORIGIN


def test_cors_allows_null_origin_when_vulnerable(user_client):
    """
    Tests that a null origin (file:// pages) is accepted
    in vulnerable mode.
    """
    toggle_harden(False)

    res = user_client.get(
        "/api/security-config",
        headers={"Origin": "null"},
    )

    assert res.headers.get("Access-Control-Allow-Origin") == "null"


def test_cors_wildcard_without_origin_when_vulnerable(user_client):
    """
    Tests that requests without an Origin header get
    Access-Control-Allow-Origin: * in vulnerable mode.
    """
    toggle_harden(False)

    res = user_client.get("/api/security-config")

    assert res.headers.get("Access-Control-Allow-Origin") == "*"


def test_cors_same_origin_works_when_vulnerable(user_client):
    """
    Tests that same-origin requests still return valid data
    in vulnerable mode (correct behavior).
    """
    toggle_harden(False)

    res = user_client.get(
        "/api/security-config",
        headers={"Origin": SAME_ORIGIN},
    )

    assert res.status_code == 200
    data = res.get_json()
    assert "authorization_enabled" in data


def test_cors_blocks_cross_origin_when_hardened(hardened_user_client):
    """
    Tests that cross-origin requests from unauthorized origins
    are blocked (403) in hardened mode.
    """
    res = hardened_user_client.get(
        "/api/security-config",
        headers={"Origin": CROSS_ORIGIN},
    )

    assert res.status_code == 403


def test_cors_blocks_null_origin_when_hardened(hardened_user_client):
    """
    Tests that null origin (file:// pages) is blocked
    in hardened mode.
    """
    res = hardened_user_client.get(
        "/api/security-config",
        headers={"Origin": "null"},
    )

    assert res.status_code == 403


def test_cors_no_wildcard_when_hardened(hardened_user_client):
    """
    Tests that the wildcard Access-Control-Allow-Origin header
    is not present in hardened mode.
    """
    res = hardened_user_client.get("/api/security-config")

    assert res.headers.get("Access-Control-Allow-Origin") != "*"


def test_cors_same_origin_works_when_hardened(hardened_user_client):
    """
    Tests that same-origin requests still succeed
    in hardened mode (correct behavior).
    """
    res = hardened_user_client.get(
        "/api/security-config",
        headers={"Origin": SAME_ORIGIN},
    )

    assert res.status_code == 200
    data = res.get_json()
    assert "authorization_enabled" in data
