import pytest
import psycopg2
import os
from app import app as flask_app
from database import init_connection_pool, init_db
import app as app_module


@pytest.fixture
def client():
    # Puts Flask into testing mode
    flask_app.config["TESTING"] = True

    init_connection_pool()
    init_db()

    # Creates Flask test client
    with flask_app.test_client() as client:
        yield client


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
