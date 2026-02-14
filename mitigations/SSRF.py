import os
import random
from urllib.parse import urlparse
import requests

ALLOWED_IMAGE_HOSTS = {"oregonstate.edu"}  # adjust to your allowlist


def _is_allowed_url(image_url: str) -> bool:
    """Verify protocol is secure and path is allowed."""
    parsed = urlparse(image_url)
    return parsed.scheme == "https" and parsed.hostname and parsed.hostname.lower() in ALLOWED_IMAGE_HOSTS


def fetch_and_store_image(image_url: str, upload_folder: str) -> tuple[str, str]:
    """Download and save image, if allowed."""
    if not _is_allowed_url(image_url):
        raise ValueError("URL not allowed")

    # Actually get the URL content
    resp = requests.get(
        image_url,
        timeout=5,
        allow_redirects=False,
        verify=True
    )

    if not resp.ok or not resp.headers.get("Content-Type", "").startswith("image/"):
        raise ValueError("Invalid image URL or response")
    
    # Generate filename and save
    filename = f"{random.randint(1, 1000000)}_{os.path.basename(urlparse(image_url).path) or 'downloaded'}"
    file_path = os.path.join(upload_folder, filename)
    with open(file_path, "wb") as f:
        f.write(resp.content)
    return filename, file_path
