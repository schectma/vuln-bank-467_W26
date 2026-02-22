# https://www.geeksforgeeks.org/python/how-to-hash-passwords-in-python/
import psycopg2
import os
import random
import hashlib
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from flask import current_app


def initialize():
    """
    Initialize the plaintext table
    and all users to it
    """
    create_plaintext_table()
    add_demo_users()
    add_existing_users()


def get_database():
    """
    ADD EXCEPTION HANDLING
    Helper function for database connection/cursor
    """

    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    return conn, conn.cursor()


def add_demo_users():
    """
    ADD EXCEPTION HANDLING
    Add hashed demo users to User table
    Most of the passwords are simple common passwords
    """
    conn, cur = get_database()

    newUsers = [
        ('hashadmin', 'Admin@123', 'HADMIN001', 1000000.0, True),
        ('hashuser1', '123456', 'HUSER001', 1000.0, False),
        ('hashuser2', 'Password', 'HUSER002', 1000.0, False),
        ('hashuser3', 'hashtesting123', 'HUSER003', 1000.0, False),
        ('hashuser4', '1234567890', 'HUSER004', 1000.0, False),
        ('hashuser5', '@kfi&mdloromb!!', 'HUSER005', 1000.0, False),
        ('hashuser6', 'P@SSw0rd', 'HUSER006', 1000.0, False),
        ('hashuser7', '@kfi&mdloromb!!', 'HUSER007', 1000.0, False),
        ('hashuser8', 'sl&nsd!gmndfg8', 'HUSER008', 1000.0, False),
        ('hashuser9', 'Aa@123456', 'HUSER009', 1000.0, False)
    ]

    for username, password, account_number, balance, is_admin in newUsers:
        cur.execute("""
            INSERT INTO users (
            username,
            password,
            account_number,
            balance,
            is_admin
            )
            VALUES
            (%s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        """, (
            username,
            password,
            account_number,
            balance,
            is_admin
        ))

    conn.commit()
    cur.close()
    conn.close()


def create_plaintext_table():
    """
    ADD EXCEPTION HANDLING
    Create a table that stores plaintext passwords
    This is needed as hashing is one way
    Therefore I cannot got from weak to medium etc. as
    The password is already hashed
    """
    conn, cur = get_database()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users_plaintext (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def add_existing_users():
    """
    ADD EXCEPTION HANDLING
    Add existing users to the plaintext table
    """
    conn, cur = get_database()

    cur.execute("""
        INSERT INTO users_plaintext (username, password)
        SELECT username, password
        FROM users
        ON CONFLICT (username) DO NOTHING
    """)

    conn.commit()
    cur.close()
    conn.close()


def create_hashing_db():
    """
    ADD EXCEPTION HANDLING
    Creates a database of hashed passwords
    """

    conn, cur = get_database()

    cur.execute("SELECT username, password FROM users_plaintext")
    rows = cur.fetchall()

    for username, password in rows:
        hpass = create_hashed_password(password)

        cur.execute("""
            UPDATE users
            SET password = %s
            WHERE username = %s
        """, (hpass, username))

        if cur.rowcount == 0:
            cur.execute("""
                INSERT INTO users (username, password)
                VALUES (%s, %s)
            """, (username, hpass))

    conn.commit()
    cur.close()
    conn.close()


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
    ADD EXCEPTION HANDLING
    Checks if the username and password match
    information in the Users table
    """
    conn, cur = get_database()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

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
