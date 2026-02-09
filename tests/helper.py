from app import app as flask_app
from database import init_connection_pool, init_db
import app as app_module

def toggle_harden(state: bool):
    """
    Helper function to toggle hardening on/off.
    """
    app_module.harden = state
    flask_app.config["HARDENED"] = state
