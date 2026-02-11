# https://www.geeksforgeeks.org/python/how-to-hash-passwords-in-python/
import psycopg2
import os
import hashlib
import bcrypt
from flask import current_app

def create_hashing_db():
    # Create a database of users with hashed passwords
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    newUsers = [
        ('hashadmin', 'Aa@123456', 'HADMIN001', 1000000.0, True),
        ('hashuser1', '123456', 'HUSER001', 1000.0, False),
        ('hashuser2', 'Password', 'HUSER002', 1000.0, False),
        ('hashuser3', 'hashtesting123', 'HUSER003', 1000.0, False),
        ('hashuser4', '1234567890', 'HUSER004', 1000.0, False),
        ('hashuser5', '@kfi&mdloromb!!', 'HUSER005', 1000.0, False),
        ('hashuser6', 'P@SSw0rd', 'HUSER006', 1000.0, False)
    ]

    for username, password, account_number, balance, is_admin in newUsers:
        password = create_hashed_password(password)

        # Insert known hashing users
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

def create_hashed_password(password):
    mode = current_app.config.get("HASHMODE", 0)

    if mode == 0:
        return password
    elif mode == 1:
        # SHA-1 Weak Hashing without salt
        return hashlib.sha1(password.encode()).hexdigest()
    elif mode == 2:
        # SHA-256 Medium Hashing without salt
        return hashlib.sha256(password.encode().hexdigest)
    elif mode == 3:
        # bcrypt Strong Hashing, automatically salts
        hpass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hpass.decode()

    return password
