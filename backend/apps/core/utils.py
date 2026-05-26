"""
Shared utility functions used across apps.
"""
import hashlib
import hmac
import secrets
import string
from typing import Any
from django.utils import timezone


def generate_secure_token(length: int = 64) -> str:
    """Generate a cryptographically secure random token."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def compute_hmac_signature(payload: str, secret: str) -> str:
    """Compute HMAC-SHA256 signature for webhook payloads."""
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def get_client_ip(request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def mask_sensitive_value(value: str, visible_chars: int = 4) -> str:
    """Mask all but the last N characters of a sensitive string."""
    if not value or len(value) <= visible_chars:
        return "****"
    return "*" * (len(value) - visible_chars) + value[-visible_chars:]


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Flatten a nested dictionary."""
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def current_year() -> int:
    return timezone.now().year


def current_quarter() -> int:
    month = timezone.now().month
    return (month - 1) // 3 + 1
