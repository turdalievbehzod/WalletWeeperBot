"""
Telegram WebApp initData validator.

Algorithm (Telegram docs):
  1. Parse initData query string into key=value pairs.
  2. Extract and remove the `hash` field.
  3. Sort remaining pairs alphabetically and join with '\\n'
     → data_check_string
  4. secret_key  = HMAC-SHA256(key=b"WebAppData", msg=bot_token)
  5. expected    = HMAC-SHA256(key=secret_key,  msg=data_check_string)
  6. Compare expected (hex) with received hash via constant-time compare
     to prevent timing attacks.
"""

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl, unquote

from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

# Reject initData older than 24 hours to prevent replay attacks.
_MAX_AUTH_AGE_SECONDS = 86_400


def validate_telegram_init_data(init_data: str) -> dict:
    """
    Validates a Telegram WebApp initData string and returns the user payload.

    Raises AuthenticationFailed on any validation failure so DRF can return
    a clean 401 response without leaking internals.
    """
    try:
        parsed: dict[str, str] = dict(parse_qsl(init_data, strict_parsing=True))
    except Exception:
        raise AuthenticationFailed('Malformed initData string.')

    received_hash = parsed.pop('hash', None)
    if not received_hash:
        raise AuthenticationFailed('initData is missing the hash field.')

    # ── Freshness check ───────────────────────────────────────────────────────
    try:
        auth_date = int(parsed['auth_date'])
    except (KeyError, ValueError):
        raise AuthenticationFailed('initData is missing auth_date.')

    if time.time() - auth_date > _MAX_AUTH_AGE_SECONDS:
        raise AuthenticationFailed('initData has expired (older than 24 h).')

    # ── Build data_check_string ───────────────────────────────────────────────
    data_check_string = '\n'.join(
        f'{k}={v}' for k, v in sorted(parsed.items())
    )

    # ── Derive secret key: HMAC-SHA256("WebAppData", bot_token) ──────────────
    secret_key = hmac.new(
        key=b'WebAppData',
        msg=settings.TELEGRAM_BOT_TOKEN.encode(),
        digestmod=hashlib.sha256,
    ).digest()

    # ── Compute expected hash ─────────────────────────────────────────────────
    expected_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison prevents timing side-channel leaks.
    if not hmac.compare_digest(expected_hash, received_hash):
        raise AuthenticationFailed('initData signature is invalid.')

    # ── Decode nested user object ─────────────────────────────────────────────
    user_raw = parsed.get('user')
    if not user_raw:
        raise AuthenticationFailed('initData contains no user object.')

    try:
        user_data: dict = json.loads(unquote(user_raw))
    except (json.JSONDecodeError, Exception):
        raise AuthenticationFailed('initData user field is not valid JSON.')

    if 'id' not in user_data:
        raise AuthenticationFailed('Telegram user object has no id field.')

    return user_data
