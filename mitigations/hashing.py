# https://www.geeksforgeeks.org/python/how-to-hash-passwords-in-python/
import psycopg2
import os
import random
import hashlib
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from flask import current_app
from contextlib import contextmanager
import urllib.parse


def initialize():
    """
    Initialize the plaintext table
    and all users to it
    """
    create_plaintext_table()
    add_demo_users()
    add_existing_users()


@contextmanager
def get_database(autocommit=False):
    """
    Helper function for database connection/cursor
    Always closes connection
    Rolls back if there is an error
    """
    conn = None

    try:
        app_env = os.getenv("APP_ENV", "production")
        database_url = os.getenv("TEST_DATABASE_URL") if app_env == "test" else os.getenv("DATABASE_URL")

        if database_url:
            parsed = urllib.parse.urlparse(database_url)
            conn = psycopg2.connect(
                dbname=parsed.path.lstrip("/"),
                user=parsed.username,
                password=parsed.password,
                host=parsed.hostname,
                port=parsed.port or 5432
            )
        else:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )

        conn.autocommit = autocommit
        with conn.cursor() as cur:
            yield conn, cur
    except psycopg2.Error:
        if conn and not autocommit:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def add_demo_users():
    """
    Add hashed demo users to User table
    Most of the passwords are simple common passwords
    """

    newUsers = [
        ('10', 'hashadmin', 'Admin@123', 'HADMIN001', 1000000.0, True),
        ('11', 'hashuser1', '123456', 'HUSER001', 1000.0, False),
        ('12', 'hashuser2', 'Password', 'HUSER002', 1000.0, False),
        ('13', 'hashuser3', 'hashtesting123', 'HUSER003', 1000.0, False),
        ('14', 'hashuser4', '1234567890', 'HUSER004', 1000.0, False),
        ('15', 'hashuser5', '@kfi&mdloromb!!', 'HUSER005', 1000.0, False),
        ('16', 'hashuser6', 'P@SSw0rd', 'HUSER006', 1000.0, False),
        ('17', 'hashuser7', '@kfi&mdloromb!!', 'HUSER007', 1000.0, False),
        ('18', 'hashuser8', 'sl&nsd!gmndfg8', 'HUSER008', 1000.0, False),
        ('19', 'hashuser9', 'Aa@123456', 'HUSER009', 1000.0, False)
    ]

    with get_database() as (conn, cur):
        for id, username, password, account_number, balance, is_admin in newUsers:
            cur.execute("""
                INSERT INTO users (
                id,
                username,
                password,
                account_number,
                balance,
                is_admin
                )
                VALUES
                (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """, (
                id,
                username,
                password,
                account_number,
                balance,
                is_admin
            ))

        conn.commit()


def create_plaintext_table():
    """
    Create a table that stores plaintext passwords
    This is needed as hashing is one way
    Therefore I cannot got from weak to medium etc. as
    The password is already hashed
    """
    with get_database() as (conn, cur):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users_plaintext (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)

        conn.commit()


def add_existing_users():
    """
    Add existing users to the plaintext table
    """
    with get_database() as (conn, cur):
        cur.execute("""
            INSERT INTO users_plaintext (username, password)
            SELECT username, password
            FROM users
            ON CONFLICT (username) DO NOTHING
        """)

        conn.commit()


def create_hashing_db():
    """
    Creates a database of hashed passwords
    """

    with get_database() as (conn, cur):
        # Clean up plaintext entries for users that no longer exist
        cur.execute("""
            DELETE FROM users_plaintext
            WHERE username NOT IN (SELECT username FROM users)
        """)

        cur.execute("SELECT username, password FROM users_plaintext")
        rows = cur.fetchall()

        for username, password in rows:
            hpass = create_hashed_password(password)

            cur.execute("""
                UPDATE users
                SET password = %s
                WHERE username = %s
            """, (hpass, username))

        conn.commit()


def create_hashed_password(password):
    """
    Hashes the passwords according to HASHMODE
    Encodes the hashing algorithm into the string
    """

    mode = current_app.config.get("HASHMODE", 0)

    if mode == 1:
        # SHA-1 Weak Hashing without salt
        return f"sha1${hashlib.sha1(password.encode()).hexdigest()}"
    elif mode == 2:
        # SHA-256 Medium Hashing without salt
        return f"sha256${hashlib.sha256(password.encode()).hexdigest()}"
    elif mode == 3:
        # Argon2id Strong Hashing, automatically salts

        ph = PasswordHasher()
        return f"argon2id${ph.hash(password)}"
    elif mode == 4:
        return password_options(password)

    return password


def password_options(password):
    """
    For the various toggle option
    Encodes the hashing algorithm into the string
    """
    sel = random.choice([1, 2, 3])

    if sel == 1:
        # SHA-1 Weak Hashing without salt
        return f"sha1${hashlib.sha1(password.encode()).hexdigest()}"
    elif sel == 2:
        # SHA-256 Medium Hashing without salt
        return f"sha256${hashlib.sha256(password.encode()).hexdigest()}"
    elif sel == 3:
        # Argon2id Strong Hashing, automatically salts
        ph = PasswordHasher()
        return f"argon2id${ph.hash(password)}"

    return password


def hashed_login(username, password):
    """
    Checks if the username and password match
    information in the Users table
    """
    with get_database() as (conn, cur):
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

    # user[2] is the password column in the database
    if not user or not check_password(user[2], password):
        return None
    return user


def check_password(stored_password, submitted_password):
    """
    Splits the encoded hashing algorithm from the password
    Compares input password with password in the database
    """
    if "$" not in stored_password:
        return False

    hash_algo, pword = stored_password.split("$", 1)

    if hash_algo == "sha1":
        return pword == hashlib.sha1(submitted_password.encode()).hexdigest()
    elif hash_algo == "sha256":
        return pword == hashlib.sha256(submitted_password.encode()).hexdigest()
    elif hash_algo == "argon2id":
        try:
            ph = PasswordHasher()
            return ph.verify(pword, submitted_password)
        except VerifyMismatchError:
            return False
        except InvalidHashError:
            return False

    return False


def save_plaintext(username, password):
    """
    When user registers, need to save plaintext password
    """
    with get_database() as (conn, cur):
        cur.execute("""
            INSERT INTO users_plaintext (username, password)
            VALUES (%s, %s)
            ON CONFLICT (username) DO UPDATE SET password = %s
        """, (username, password, password))
        conn.commit()
