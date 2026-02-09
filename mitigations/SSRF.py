import os
import random
import ipaddress
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
import requests

ALLOWED_IMAGE_HOSTS = {"oregonstate.edu"}  # adjust to your allowlist


def _is_private_address(hostname: str) -> bool:
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast
    except ValueError:
        return False


def _is_allowed_url(image_url: str) -> bool:
    try:
        parsed = urlparse(image_url)
        if parsed.scheme != "https":
            return False
        if not parsed.hostname:
            return False
        host = parsed.hostname.lower()
        if _is_private_address(host):
            return False
        if host not in ALLOWED_IMAGE_HOSTS:
            return False
        return True
    except Exception:
        return False


def fetch_and_store_image(image_url: str, upload_folder: str) -> tuple[str, str]:
    if not _is_allowed_url(image_url):
        raise ValueError("URL not allowed")

    resp = requests.get(
        image_url,
        timeout=5,
        allow_redirects=False,
        verify=True
    )
    if resp.status_code >= 400:
        raise ValueError(f"Failed to fetch URL: HTTP {resp.status_code}")

    content_type = resp.headers.get("Content-Type", "")
    if not content_type.startswith("image/"):
        raise ValueError("URL did not return an image")

    content = resp.content

    parsed = urlparse(image_url)
    basename = os.path.basename(parsed.path) or "downloaded"
    filename = secure_filename(basename)
    filename = f"{random.randint(1, 1000000)}_{filename}"
    file_path = os.path.join(upload_folder, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    return filename, file_path
