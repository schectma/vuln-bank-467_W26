import tempfile
import pytest
from mitigations.SSRF import fetch_and_store_image


def test_fetch_and_store_image_disallowed_url():
    """Should raise ValueError for disallowed URLs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        url = "https://example.com/image.png"
        with pytest.raises(ValueError, match="URL not allowed"):
            fetch_and_store_image(url, tmpdir)


def test_fetch_and_store_image_allowed_url_invalid_image():
    """Should raise ValueError for allowed URL that does not return an image."""
    with tempfile.TemporaryDirectory() as tmpdir:
        url = "https://oregonstate.edu/not-an-image"
        with pytest.raises(ValueError):
            fetch_and_store_image(url, tmpdir)
