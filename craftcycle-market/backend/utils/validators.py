"""
craftcycle/backend/app/utils/validators.py
────────────────────────────────────────────
Reusable input validation functions used across routes.
"""
import re


# ── Email ─────────────────────────────────────────────────────
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip().lower()))


# ── Password ──────────────────────────────────────────────────
def validate_password(password: str) -> tuple[bool, str]:
    """
    Returns (is_valid, error_message).
    Rules: 8+ chars, at least one uppercase, lowercase, and digit.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    return True, ""


# ── Username ──────────────────────────────────────────────────
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,30}$")

def validate_username(username: str) -> tuple[bool, str]:
    if not USERNAME_RE.match(username):
        return False, "Username must be 3–30 characters (letters, numbers, underscore)."
    return True, ""


# ── String sanitisation ───────────────────────────────────────
def sanitize_string(value: str, max_len: int = 500) -> str:
    """Strip whitespace and truncate to max_len."""
    return value.strip()[:max_len] if value else ""


# ── Positive number ───────────────────────────────────────────
def is_positive_number(value) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False
