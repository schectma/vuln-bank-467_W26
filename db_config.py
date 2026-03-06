import os
from urllib.parse import urlparse

def build_db_config():
    """Select and set actual database used upon launch of app.
    Dependent on state of USE_TEST_DB, which is set in test_sqli.py.
    """
    use_test_db = os.getenv("USE_TEST_DB", "").lower() in {"1", "true", "yes", "y"}
    test_db_url = os.getenv("TEST_DATABASE_URL")

    if use_test_db and test_db_url:
        parsed = urlparse(test_db_url)
        return {
            "dbname": parsed.path.lstrip("/"),
            "user": parsed.username,
            "password": parsed.password,
            "host": parsed.hostname,
            "port": str(parsed.port or 5432),
        }

    return {
        "dbname": os.getenv("DB_NAME", "vulnerable_bank"),
        "user": os.getenv("DB_USER", "vuln_user"),
        "password": os.getenv("DB_PASSWORD", "vulnbank123"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
    }