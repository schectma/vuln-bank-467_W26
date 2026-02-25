import pytest
import hashlib
from app import app as flask_app
from mitigations import hashing


@pytest.fixture
def hash_client(client, setup_test_db, setup_plaintext_db):
    """
    Provides a test client whose DB already has the plaintext table seeded.
    setup_plaintext_db depends on setup_test_db, so the users table is
    populated with known test users (admin, testuser1, testuser2, testuser3).
    """
    return client


def _hash_and_login(client, mode, username, password):
    """
    Helper: set HASHMODE, hash the DB, then POST /login.
    Returns the response object.
    """
    flask_app.config["HASHMODE"] = mode

    with flask_app.app_context():
        hashing.create_hashing_db()

    return client.post("/login", json={
        "username": username,
        "password": password,
    })


# Tests if each mode is hashing correctly
def test_mode0_returns_plaintext(hash_client):
    """HASHMODE 0 should return the password unchanged."""
    flask_app.config["HASHMODE"] = 0
    with flask_app.app_context():
        result = hashing.create_hashed_password("hello")
    assert result == "hello"


def test_mode1_sha1(hash_client):
    """HASHMODE 1 should return sha1$<hex>."""
    flask_app.config["HASHMODE"] = 1
    with flask_app.app_context():
        result = hashing.create_hashed_password("hello")
    expected = f"sha1${hashlib.sha1(b'hello').hexdigest()}"
    assert result == expected


def test_mode2_sha256(hash_client):
    """HASHMODE 2 should return sha256$<hex>."""
    flask_app.config["HASHMODE"] = 2
    with flask_app.app_context():
        result = hashing.create_hashed_password("hello")
    expected = f"sha256${hashlib.sha256(b'hello').hexdigest()}"
    assert result == expected


def test_mode3_argon2id(hash_client):
    """HASHMODE 3 should return argon2id$<argon2 hash>."""
    flask_app.config["HASHMODE"] = 3
    with flask_app.app_context():
        result = hashing.create_hashed_password("hello")
    assert result.startswith("argon2id$")
    assert "$argon2id$" in result


def test_mode4_random_choice(hash_client):
    """HASHMODE 4 should return one of sha1$, sha256$, or argon2id$."""
    flask_app.config["HASHMODE"] = 4
    valid_prefixes = ("sha1$", "sha256$", "argon2id$")
    with flask_app.app_context():
        result = hashing.create_hashed_password("hello")
    assert result.startswith(valid_prefixes), (
        f"Expected one of {valid_prefixes}, got: {result}"
    )


# Tests if can login with correct credentials in each mode
@pytest.mark.parametrize("mode", [1, 2, 3, 4])
def test_login_success_each_mode(hash_client, mode):
    """
    Hash passwords with the given mode, then log in with correct
    credentials — should return 200 with a token.
    """
    res = _hash_and_login(hash_client, mode, "testuser1", "testpassword1")
    data = res.get_json()
    assert res.status_code == 200
    assert data["status"] == "success"
    assert "token" in data


@pytest.mark.parametrize("mode", [1, 2, 3, 4])
def test_login_wrong_password(hash_client, mode):
    """Login with an incorrect password should return 401."""
    res = _hash_and_login(hash_client, mode, "admin", "wrongpassword")
    assert res.status_code == 401


@pytest.mark.parametrize("mode", [1, 2, 3, 4])
def test_login_nonexistent_user(hash_client, mode):
    """Login with a username that doesn't exist should return 401."""
    res = _hash_and_login(hash_client, mode, "ghost", "whatever")
    assert res.status_code == 401
