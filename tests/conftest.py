import pytest
import psycopg2
import os
from app import app as flask_app
from database import init_connection_pool, init_db
import app as app_module
from helper import toggle_harden


@pytest.fixture
def client():
    # Puts Flask into testing mode
    flask_app.config["TESTING"] = True

    init_connection_pool()
    init_db()

    # Creates Flask test client
    with flask_app.test_client() as client:
        yield client


def _login(client, username, password, hardened):
    """
    Internal helper that toggles harden state, logs in, and attaches
    the JWT token to the client's Authorization header.
    """
    toggle_harden(hardened)

    res = client.post("/login", json={
        "username": username,
        "password": password
    })

    assert res.status_code == 200, (
        f"Login failed for '{username}' (hardened={hardened}): "
        f"{res.status_code} {res.get_json()}"
    )

    token = res.get_json().get("token")
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"

    return client


@pytest.fixture
def admin_client(client, setup_test_db):
    """
    Logged in as admin in vulnerable (unhardened) mode.

    Usage:
        def test_something(admin_client):
            res = admin_client.post("/admin/create_admin", json={...})
    """
    return _login(
        client,
        username="admin",
        password="admin123",
        hardened=False
    )


@pytest.fixture
def hardened_admin_client(client, setup_test_db):
    """
    Logged in as admin in hardened mode.

    Usage:
        def test_something(hardened_admin_client):
            res = hardened_admin_client.post("/admin/create_admin", json={...})
    """
    return _login(
        client,
        username="admin",
        password="admin123",
        hardened=True
    )


@pytest.fixture
def user_client(client, setup_test_db):
    """
    Logged in as a non-admin user (testuser1) in vulnerable (unhardened) mode.

    Usage:
        def test_something(user_client):
            res = user_client.get("/some/route")
    """
    return _login(
        client, username="testuser1",
        password="testpassword1",
        hardened=False
    )


@pytest.fixture
def hardened_user_client(client, setup_test_db):
    """
    Logged in as a non-admin user (testuser1) in hardened mode.

    Usage:
        def test_something(hardened_user_client):
            res = hardened_user_client.get("/some/route")
    """
    return _login(
        client,
        username="testuser1",
        password="testpassword1",
        hardened=True
    )


# Create test database
@pytest.fixture(scope="session", autouse=True)
def ensure_test_db():
    """
    Runs once before any tests.
    Creates the test database if it doesn't exist.
    """
    main_db_url = os.getenv("DATABASE_URL")
    test_db_url = os.getenv("TEST_DATABASE_URL")

    assert main_db_url, "DATABASE_URL not set"
    assert test_db_url, "TEST_DATABASE_URL not set"

    # Connect to main postgres server
    conn = psycopg2.connect(main_db_url)
    conn.autocommit = True
    cur = conn.cursor()

    test_db_name = test_db_url.split("/")[-1]

    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (test_db_name,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(f"CREATE DATABASE {test_db_name};")
        print(f"[pytest] Created test database: {test_db_name}")

    cur.close()
    conn.close()

    yield

    # Delete the test database
    conn = psycopg2.connect(main_db_url)
    conn.autocommit = True
    cur = conn.cursor()

    # Disconnect users from DB before dropping
    cur.execute("""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = %s;
    """, (test_db_name,))

    cur.execute(f"DROP DATABASE IF EXISTS {test_db_name};")
    print(f"[pytest] Dropped test database: {test_db_name}")

    cur.close()
    conn.close()


# Add whatever information needs to be in the test database here
@pytest.fixture(scope="function")
def setup_test_db():
    # Clear rate limiting state before each test
    app_module.rate_limit_storage.clear()
    # Runs before each test
    db_url = os.getenv("TEST_DATABASE_URL")
    assert db_url, "TEST_DATABASE_URL not set"

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Ensure users table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            account_number TEXT NOT NULL UNIQUE,
            balance DECIMAL(15, 2) DEFAULT 1000.0,
            is_admin BOOLEAN DEFAULT FALSE,
            profile_picture TEXT,
            reset_pin TEXT
        );
    """)

    # Reset table data
    cur.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE;")

    # Insert known test users
    cur.execute("""
        INSERT INTO users (
        username,
        password,
        account_number,
        balance,
        is_admin
        )
        VALUES
        ('admin', 'admin123', 'ADMIN001', 1000000.0, True),
        ('testuser1', 'testpassword1', 'TEST001', 1000.0, False),
        ('testuser2', 'testpassword2', 'TEST002', 1000.0, False),
        ('testuser3', 'testpassword3', 'TEST003', 1000.0, False);
    """)

    conn.commit()
    cur.close()
    conn.close()

    yield

    app_module.harden = False


@pytest.fixture
def setup_transactions_db():
    """
    Creates a test transactions database

    Usage:
        def test_something(user_client, setup_transactions_db):
            res = user_client.get("/api/transactions?account_number=TEST001")
    """
    db_url = os.getenv("TEST_DATABASE_URL")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            from_account TEXT NOT NULL,
            to_account TEXT NOT NULL,
            amount DECIMAL(15, 2) NOT NULL,
            timestamp TIMESTAMP DEFAULT NOW(),
            transaction_type TEXT NOT NULL,
            description TEXT
        );
    """)

    cur.execute("TRUNCATE TABLE transactions RESTART IDENTITY;")

    cur.execute("""
        INSERT INTO transactions
            (from_account, to_account, amount, transaction_type, description)
        VALUES
            ('TEST001', 'TEST002', 100.00, 'transfer', 'Test transfer 1'),
            ('TEST002', 'TEST001', 50.00,  'transfer', 'Test transfer 2'),
            ('TEST001', 'TEST003', 25.00,  'transfer', 'Test transfer 3');
    """)

    conn.commit()
    cur.close()
    conn.close()

    yield


@pytest.fixture
def setup_virtual_cards_db():
    """
    Sets the virtual_cards table

    Inserts:
        - card id=1 belonging to testuser1 (TEST001)
        - card id=2 belonging to testuser2 (TEST002)

    Usage:
        def test_something(user_client, setup_virtual_cards_db):
            res = user_client.post("/api/virtual-cards/1/toggle-freeze")
    """
    db_url = os.getenv("TEST_DATABASE_URL")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute("TRUNCATE TABLE virtual_cards RESTART IDENTITY CASCADE;")

    cur.execute("""
        INSERT INTO virtual_cards(
            user_id,
            card_number,
            cvv,
            expiry_date,
            card_limit,
            card_type,
            is_frozen
        )
        VALUES
            (
            2,
            '1111222233334444',
            '123',
            '12/26',
            1000.00,
            'standard',
            FALSE
            ),
            (
            3,
            '5555666677778888',
            '456',
            '12/26',
            1000.00,
            'standard',
            FALSE
            );
    """)

    conn.commit()
    cur.close()
    conn.close()

    yield


def setup_bill_payments_db():
    """
    Sets the bill payments table.

    Usage:
        def test_something(user_client, setup_bill_payments_db):
            res = user_client.get("/api/bill-payments/history")
    """
    db_url = os.getenv("TEST_DATABASE_URL")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Seed one virtual card for testuser1 to use in a card payment
    cur.execute("TRUNCATE TABLE virtual_cards RESTART IDENTITY CASCADE;")
    cur.execute("""
        INSERT INTO virtual_cards
            (
            user_id,
            card_number,
            cvv,
            expiry_date,
            card_limit,
            card_type,
            is_frozen
            )
        VALUES
            (
            2,
            '1111222233334444',
            '123',
            '12/26',
            1000.00,
            'standard',
            FALSE
            );
    """)

    cur.execute("TRUNCATE TABLE bill_payments RESTART IDENTITY CASCADE;")
    cur.execute("""
        INSERT INTO bill_payments
            (
            user_id,
            biller_id,
            amount,
            payment_method,
            card_id,
            reference_number,
            status,
            description
            )
        VALUES
            (
            2,
            1,
            75.00,
            'balance',
            NULL,
            'REF001',
            'completed',
            'Water bill payment'
            ),
            (2,
            2,
            120.00,
            'virtual_card',
            1,
            'REF002',
            'completed',
            'Electric bill payment'
            );
    """)

    conn.commit()
    cur.close()
    conn.close()

    yield


@pytest.fixture
def user_exists():
    """
    Helper function to tests if user exists
    This is to help with testing SQL injections
    """
    def _user_exists(username):
        conn = psycopg2.connect(os.getenv("TEST_DATABASE_URL"))
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM users WHERE username = %s;", (username,))
        exists = cur.fetchone() is not None

        cur.close()
        conn.close()

        return exists

    return _user_exists
