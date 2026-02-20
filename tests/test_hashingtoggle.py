from app import app as flask_app


def test_default_hashmode(client, setup_test_db):
    """
    Tests that the default hashmode is 0 (Plaintext).
    """
    flask_app.config["HASHMODE"] = 0

    res = client.get("/api/hashmode")
    data = res.get_json()

    assert res.status_code == 200
    assert data["hashmode"] == 0
    assert data["modename"] == "None - Plaintext"


def test_toggle_to_mode1(client, setup_test_db, setup_plaintext_db):
    """
    Tests toggling from 0 to 1 (Weak - SHA-1).
    """
    flask_app.config["HASHMODE"] = 0

    res = client.post("/api/toggle/hashing")
    data = res.get_json()

    assert data["status"] == "success"
    assert data["hashmode"] == 1

    res = client.get("/api/hashmode")
    assert res.get_json()["modename"] == "Weak - SHA-1"


def test_toggle_to_mode2(client, setup_test_db, setup_plaintext_db):
    """
    Tests toggling from 1 to 2 (Medium - SHA-256).
    """
    flask_app.config["HASHMODE"] = 1

    res = client.post("/api/toggle/hashing")
    data = res.get_json()

    assert data["status"] == "success"
    assert data["hashmode"] == 2

    res = client.get("/api/hashmode")
    assert res.get_json()["modename"] == "Medium - SHA-256"


def test_toggle_to_mode3(client, setup_test_db, setup_plaintext_db):
    """
    Tests toggling from 2 to 3 (Strong - Argon2id).
    """
    flask_app.config["HASHMODE"] = 2

    res = client.post("/api/toggle/hashing")
    data = res.get_json()

    assert data["status"] == "success"
    assert data["hashmode"] == 3

    res = client.get("/api/hashmode")
    assert res.get_json()["modename"] == "Strong - Argon2id"


def test_toggle_to_mode4(client, setup_test_db, setup_plaintext_db):
    """
    Tests toggling from 3 to 4 (Various Types).
    """
    flask_app.config["HASHMODE"] = 3

    res = client.post("/api/toggle/hashing")
    data = res.get_json()

    assert data["status"] == "success"
    assert data["hashmode"] == 4

    res = client.get("/api/hashmode")
    assert res.get_json()["modename"] == "Various Types"


def test_toggle_wraps_to_mode0(client, setup_test_db, setup_plaintext_db):
    """
    Tests toggling from 4 wraps back to 0 (Plaintext).
    """
    flask_app.config["HASHMODE"] = 4

    res = client.post("/api/toggle/hashing")
    data = res.get_json()

    assert data["status"] == "success"
    assert data["hashmode"] == 0

    res = client.get("/api/hashmode")
    assert res.get_json()["modename"] == "None - Plaintext"
