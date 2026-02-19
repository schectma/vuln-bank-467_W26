import psycopg2
import os

# This file makes sure that all of the tables have data as expected.


def get_db():
    return psycopg2.connect(os.getenv("TEST_DATABASE_URL"))


<<<<<<< test_table_virtual_cards
def test_virtual_cards_table_exists(setup_test_db):
    """Confirms the virtual_cards table exists in the test database."""
=======
def test_users_table_exists(setup_test_db):
    """Confirms the users table exists in the test database."""
>>>>>>> prelim
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM information_schema.tables
<<<<<<< test_table_virtual_cards
        WHERE table_name = 'virtual_cards';
=======
        WHERE table_name = 'users';
>>>>>>> prelim
    """)
    assert cur.fetchone() is not None
    cur.close()
    conn.close()


<<<<<<< test_table_virtual_cards
def test_virtual_cards_table_seeded(setup_virtual_cards_db):
    """Confirms setup_virtual_cards_db inserts the expected test cards."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM virtual_cards;")
=======
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
>>>>>>> prelim
    count = cur.fetchone()[0]
    cur.close()
    conn.close()

<<<<<<< test_table_virtual_cards
    assert count == 2
=======
    assert count == 3
>>>>>>> prelim
