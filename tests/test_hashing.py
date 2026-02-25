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


# Tests for registration
def _hash_register(client, mode, username, password):
    """
    Helper: set HASHMODE, then POST /register.
    Returns the response object.
    """
    flask_app.config["HASHMODE"] = mode

    return client.post("/register", json={
        "username": username,
        "password": password,
    })


def _get_stored_password(username):
    """Fetch the hashed password from the users table."""
    with hashing.get_database() as (conn, cur):
        cur.execute(
            "SELECT password FROM users WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()
    return row[0] if row else None


def _get_plaintext_password(username):
    """Fetch the plaintext password from the users_plaintext table."""
    with hashing.get_database() as (conn, cur):
        cur.execute(
            "SELECT password FROM users_plaintext WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()
    return row[0] if row else None


# Tests if registration stores a hashed password in each mode
@pytest.mark.parametrize("mode,prefix", [
    (1, "sha1$"),
    (2, "sha256$"),
    (3, "argon2id$"),
])
def test_register_password_is_hashed(hash_client, mode, prefix):
    """
    Registered user's password in the DB should
    start with the correct hash prefix.
    """
    uname = f"newuser_{mode}"
    res = _hash_register(hash_client, mode, uname, "newpass123")
    assert res.status_code == 200

    stored = _get_stored_password(uname)
    assert stored is not None
    assert stored.startswith(prefix), (
        f"Expected prefix '{prefix}', got: {stored[:30]}"
    )


def test_register_mode4_password_is_hashed(hash_client):
    """Mode 4 should store one of the three hash formats."""
    res = _hash_register(hash_client, 4, "newuser4", "newpass123")
    assert res.status_code == 200

    stored = _get_stored_password("newuser4")
    assert stored is not None
    valid_prefixes = ("sha1$", "sha256$", "argon2id$")
    assert stored.startswith(valid_prefixes), (
        f"Expected one of {valid_prefixes}, got: {stored[:30]}"
    )


# Tests if plaintext password is saved alongside the hash
@pytest.mark.parametrize("mode", [1, 2, 3, 4])
def test_register_saves_plaintext(hash_client, mode):
    """
    Registration should also store the
    original password in users_plaintext.
    """
    uname = f"ptuser{mode}"
    res = _hash_register(hash_client, mode, uname, "myplainpass")
    assert res.status_code == 200

    plaintext = _get_plaintext_password(uname)
    assert plaintext == "myplainpass"


@pytest.mark.parametrize("mode", [1, 2, 3, 4])
def test_register_then_login(hash_client, mode):
    """
    Register a new user with hashing, then log in
    with the correct credentials.
    """
    uname = f"reglogin{mode}"
    pwd = "Str0ngP@ss!"

    reg = _hash_register(hash_client, mode, uname, pwd)
    assert reg.status_code == 200

    # Login — no need to call create_hashing_db because
    # register already hashed
    flask_app.config["HASHMODE"] = mode
    login = hash_client.post("/login", json={
        "username": uname,
        "password": pwd,
    })
    data = login.get_json()
    assert login.status_code == 200
    assert data["status"] == "success"
    assert "token" in data
