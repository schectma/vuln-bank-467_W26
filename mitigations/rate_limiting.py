from functools import wraps
from flask import jsonify, request, current_app

# Necessary so decorator can use helpers from app.py without importing app.py
_get_client_ip = None
_check_rate_limit = None


def init_rate_limiting(get_client_ip, check_rate_limit):
    """Adds helper functions from app.py without importing app.py."""
    global _get_client_ip, _check_rate_limit
    _get_client_ip = get_client_ip
    _check_rate_limit = check_rate_limit


def ip_rate_limit(prefix: str, limit: int):
    """Rate limiting decorator that uses IP to enforce hardening toggle."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_app.config.get("HARDENED", False):
                return f(*args, **kwargs)

            # Prevents rate limiting from affecting future logins in demo
            if request.method != "POST":
                return f(*args, **kwargs)

            client_ip = _get_client_ip()
            key = f"{prefix}_ip_{client_ip}"
            allowed, count, lim = _check_rate_limit(key, limit)

            if not allowed:
                return jsonify({
                    "status": "error",
                    "message": f"Too many requests. Rate limit: {lim}.",
                    "rate_limit_info": {
                        "limit_type": "ip",
                        "client_ip": client_ip,
                        "current_count": count,
                        "limit": lim,
                        "window_hours": 3
                    }
                }), 429

            return f(*args, **kwargs)
        return wrapped
    return decorator
