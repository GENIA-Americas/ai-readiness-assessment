"""
Per-org API key authentication.

This is deliberately minimal, not a full user-account system, because the
threat this addresses is narrow: with no auth at all, any client on the
public internet could enumerate/list every org's data. A single shared
API key would only half-fix that (a leaked key still exposes every org
to every other org); a full login system is disproportionate for a tool
with no human end users, only server-to-server callers.

So: each API key maps to exactly one org. A key authenticates a caller as
that org and nothing else. Ownership checks (see routers/assessments.py)
then ensure a caller can only ever create, read, or list records under
their own org.

Keys are read from the API_KEYS env var as "key1:org_one,key2:org_two".
"""
import hmac
import os

from fastapi import Header, HTTPException, status


def _load_api_keys() -> dict[str, str]:
    raw = os.getenv("API_KEYS", "")
    keys: dict[str, str] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair:
            continue
        key, _, org = pair.partition(":")
        if key and org:
            keys[key] = org
    return keys


_API_KEYS = _load_api_keys()

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or missing API key",
    headers={"WWW-Authenticate": "X-API-Key"},
)


def get_current_org(x_api_key: str | None = Header(None, alias="X-API-Key")) -> str:
    """
    FastAPI dependency. Validates X-API-Key against configured keys using a
    constant-time comparison per key (avoids leaking key length/prefix via
    timing), and returns the org name that key belongs to.

    Header is declared optional (default None) rather than required,
    specifically so a missing header and a wrong header both reach this
    function and both return the same 401 — otherwise FastAPI's own
    request validation intercepts a missing required header and returns
    422 before this code ever runs, which is a confusing inconsistency
    for an auth check.
    """
    if x_api_key is None:
        raise _UNAUTHORIZED

    for known_key, org_name in _API_KEYS.items():
        if hmac.compare_digest(x_api_key, known_key):
            return org_name

    raise _UNAUTHORIZED
