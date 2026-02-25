import os
from conftest import pg_connect

# This file makes sure that all of the tables have data as expected.

db_url = os.getenv("TEST_DATABASE_URL")


def _table_exists(table_name):
    with pg_connect(db_url) as (conn, cur):
        cur.execute("""
            SELECT 1 FROM information_schema.tables
            WHERE table_name = %s;
        """, (table_name,))
        return cur.fetchone() is not None


def _row_count(table_name):
    with pg_connect(db_url) as (conn, cur):
        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        return cur.fetchone()[0]


def test_users_table_exists(setup_test_db):
    """Confirms the users table exists in the test database."""
    assert _table_exists("users")


def test_users_table_seeded(setup_test_db):
    """Confirms setup_test_db inserts the expected test users."""
    with pg_connect(db_url) as (conn, cur):
        cur.execute("SELECT username FROM users ORDER BY id;")
        usernames = [row[0] for row in cur.fetchall()]
    assert usernames == ["admin", "testuser1", "testuser2", "testuser3"]


def test_transactions_table_exists(setup_test_db):
    """Confirms the transactions table exists in the test database."""
    assert _table_exists("transactions")


def test_transactions_table_seeded(setup_transactions_db):
    """Confirms setup_transactions_db inserts the expected test rows."""
    assert _row_count("transactions") == 3


def test_virtual_cards_table_exists(setup_test_db):
    """Confirms the virtual_cards table exists in the test database."""
    assert _table_exists("virtual_cards")


def test_virtual_cards_table_seeded(setup_virtual_cards_db):
    """Confirms setup_virtual_cards_db inserts the expected test cards."""
    assert _row_count("virtual_cards") == 2


def test_bill_payments_table_exists(setup_test_db):
    """Confirms the bill_payments table exists in the test database."""
    assert _table_exists("bill_payments")


def test_bill_payments_table_seeded(setup_bill_payments_db):
    """Confirms setup_bill_payments_db inserts the expected test rows."""
    assert _row_count("bill_payments") == 2


def test_loans_table_exists(client, setup_test_db):
    """
    Confirms the loans table exists in the test database.
    No additional data was inserted into this table in conftest
    """
    assert _table_exists("loans")


def test_ctransactions_table_exists(client, setup_test_db):
    """
    Confirms the card transactions table exists in the test database.
    No additional data was inserted into this table in conftest
    """
    assert _table_exists("card_transactions")


def test_bill_categories_table_exists(client, setup_test_db):
    """
    Confirms the bill categories table exists in the test database.
    No additional data was inserted into this table in conftest
    """
    assert _table_exists("bill_categories")


def test_billers_table_exists(client, setup_test_db):
    """
    Confirms the billers table exists in the test database.
    No additional data was inserted into this table in conftest
    """
    assert _table_exists("billers")
