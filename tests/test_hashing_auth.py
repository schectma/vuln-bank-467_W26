import pytest
import os
import psycopg2
from mitigations import hashing
from app import app


@pytest.fixture
def set_hashmode():
    """
    Sets HASHMODE directly and rebuilds the hashed database.
    """
    def _set(mode):
        with app.app_context():
            app.config["HASHMODE"] = mode
            hashing.create_hashing_db()
    return _set


@pytest.mark.parametrize("mode", [1, 2, 3, 4])
def test_login_success_all_hash_modes(
    client,
    setup_test_db,
    setup_plaintext_db,
    set_hashmode,
    mode
):
    """
    Tests if can log into app with correct
    credentials in all hashmodes
    """
    set_hashmode(mode)

    res = client.post("/login", json={
        "username": "testuser1",
        "password": "testpassword1"
    })

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "token" in data


@pytest.mark.parametrize("mode", [1, 2, 3, 4])
def test_login_wrong_password_fails(
    client,
    setup_test_db,
    setup_plaintext_db,
    set_hashmode,
    mode
):
    """
    Tests if can log into app with incorrect
    credentials in all hashmodes
    """
    set_hashmode(mode)

    res = client.post("/login", json={
        "username": "testuser1",
        "password": "wrongpassword"
    })

    assert res.status_code == 401


@pytest.mark.parametrize("mode,prefix", [
    (1, "sha1$"),
    (2, "sha256$"),
    (3, "argon2id$"),
])
def test_passwords_are_hashed_correctly(
    setup_test_db,
    setup_plaintext_db,
    set_hashmode,
    mode,
    prefix
):
    """
    Tests if passwords are hashed according to mode
    """
    set_hashmode(mode)

    conn = psycopg2.connect(os.getenv("TEST_DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("""
        SELECT password FROM users
        WHERE username = 'testuser1'
    """)
    stored_password = cur.fetchone()[0]

    cur.close()
    conn.close()

    assert stored_password.startswith(prefix)


def test_various_mode_hashes_login(
    client,
    setup_test_db,
    setup_plaintext_db,
    set_hashmode
):
    """
    Tests that passwords are hashed in Various mode
    """
    set_hashmode(4)

    res = client.post("/login", json={
        "username": "testuser1",
        "password": "testpassword1"
    })

    assert res.status_code == 200

    # Confirm password is not plaintext
    conn = psycopg2.connect(os.getenv("TEST_DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("""
        SELECT password FROM users
        WHERE username = 'testuser1'
    """)
    stored_password = cur.fetchone()[0]

    cur.close()
    conn.close()

    assert "$" in stored_password
    assert not stored_password == "testpassword1"
