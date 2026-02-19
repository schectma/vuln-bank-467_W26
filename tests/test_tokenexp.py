import jwt
from helper import toggle_harden
from auth import JWT_SECRET
from datetime import datetime, timedelta


PROTECTED_ENDPOINT = "/check_balance/TEST001"


def test_token_vuln_valid(user_client, setup_test_db):
    """
    Tests that a valid token works in vulnerable mode
    """
    toggle_harden(False)

    res = user_client.get(PROTECTED_ENDPOINT)

    assert res.status_code == 200


def test_token_vuln_expired(client, setup_test_db):
    """
    Tests that old token still works in vulnerable mode
    """
    toggle_harden(False)

    # Login to get a token
    # Using client to get access to the token
    res = client.post("/login", json={
        "username": "testuser1",
        "password": "testpassword1"
    })
    token = res.get_json()["token"]

    # Decode and confirm there is no exp claim
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    assert "exp" not in payload

    # Simulate waiting past the hardened expiry window
    # by manually creating a token with an iat in the past
    old_payload = {
        "user_id": payload["user_id"],
        "username": payload["username"],
        "is_admin": payload["is_admin"],
        "iat": payload["iat"],
    }
    old_token = jwt.encode(old_payload, JWT_SECRET, algorithm="HS256")

    # Token should still work because there is no exp claim
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {old_token}"
    res = client.get(PROTECTED_ENDPOINT)

    assert res.status_code == 200


def test_token_hardened_valid(hardened_user_client, setup_test_db):
    """
    Tests that a valid token works in hardened mode
    """
    res = hardened_user_client.get(PROTECTED_ENDPOINT)

    assert res.status_code == 200


def test_token_hardened_contains_expired(client, setup_test_db):
    """
    Tests that a hardened token includes the exp claim.
    """
    toggle_harden(True)

    res = client.post("/login", json={
        "username": "testuser1",
        "password": "testpassword1"
    })
    token = res.get_json()["token"]

    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    assert "exp" in payload


def test_token_hardened_invalid(client, setup_test_db):
    """
    Tests that a hardened token is rejected after it expires.
    """
    toggle_harden(True)

    expired_payload = {
        "user_id": 2,
        "username": "testuser1",
        "is_admin": False,
        "iat": datetime.utcnow() - timedelta(seconds=60),
        "exp": datetime.utcnow() - timedelta(seconds=30),
    }
    expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm="HS256")

    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {expired_token}"
    res = client.get(PROTECTED_ENDPOINT)

    assert res.status_code == 401
    assert res.get_json()["error"] == "Token has expired"


def test_token_hardened_rejects_no_exp(client, setup_test_db):
    """
    Tests that hardened mode rejects a token missing the exp claim.
    """
    toggle_harden(True)

    no_exp_payload = {
        "user_id": 2,
        "username": "testuser1",
        "is_admin": False,
        "iat": 1700000000,
    }
    token = jwt.encode(no_exp_payload, JWT_SECRET, algorithm="HS256")

    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    res = client.get(PROTECTED_ENDPOINT)

    assert res.status_code == 401
