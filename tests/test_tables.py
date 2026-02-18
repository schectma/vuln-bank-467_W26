import psycopg2
import os

# This file makes sure that all of the tables have data as expected.


def get_db():
    return psycopg2.connect(os.getenv("TEST_DATABASE_URL"))


def test_virtual_cards_table_exists(setup_test_db):
    """Confirms the virtual_cards table exists in the test database."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'virtual_cards';
    """)
    assert cur.fetchone() is not None
    cur.close()
    conn.close()


def test_virtual_cards_table_seeded(setup_virtual_cards_db):
    """Confirms setup_virtual_cards_db inserts the expected test cards."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM virtual_cards;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()

    assert count == 2
