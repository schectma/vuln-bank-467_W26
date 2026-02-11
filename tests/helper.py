from app import app as flask_app
import app as app_module


def toggle_harden(state: bool):
    """
    Helper function to toggle hardening on/off.
    """
    app_module.harden = state
    flask_app.config["HARDENED"] = state
