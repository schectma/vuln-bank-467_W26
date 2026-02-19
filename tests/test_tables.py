import psycopg2
import os

# This file makes sure that all of the tables have data as expected.


def get_db():
    return psycopg2.connect(os.getenv("TEST_DATABASE_URL"))


def test_users_table_exists(setup_test_db):
    """Confirms the users table exists in the test database."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'users';
    """)
    assert cur.fetchone() is not None
    cur.close()
    conn.close()


def test_users_table_seeded(setup_test_db):
    """Confirms setup_test_db inserts the expected test users."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users ORDER BY id;")
    usernames = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    assert usernames == ["admin", "testuser1", "testuser2", "testuser3"]


def test_transactions_table_exists(setup_test_db):
    """Confirms the transactions table exists in the test database."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'transactions';
    """)
    assert cur.fetchone() is not None
    cur.close()
    conn.close()


def test_transactions_table_seeded(setup_transactions_db):
    """Confirms setup_transactions_db inserts the expected test rows."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM transactions;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()

    assert count == 3


def test_bill_payments_table_exists(setup_test_db):
    """Confirms the bill_payments table exists in the test database."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'bill_payments';
    """)
    assert cur.fetchone() is not None
    cur.close()
    conn.close()


def test_bill_payments_table_seeded(setup_bill_payments_db):
    """Confirms setup_bill_payments_db inserts the expected test rows."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM bill_payments;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()

    assert count == 2
