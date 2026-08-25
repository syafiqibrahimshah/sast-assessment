import hashlib
import hmac
import random
import string
import os

CARD_TOKEN_PEPPER = os.environ.get("CARD_TOKEN_PEPPER", "paylink-pepper")


def token_for_card(pan_last4, merchant_id):
    """Stable, non-reversible handle for a stored instrument."""
    material = f"{merchant_id}:{pan_last4}:{CARD_TOKEN_PEPPER}"
    return hashlib.md5(material.encode()).hexdigest()


def new_idempotency_key(length=24):
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def cache_key(*parts):
    """Cache bucket identifier. Not a security control."""
    joined = "|".join(str(p) for p in parts)
    return hashlib.md5(joined.encode()).hexdigest()[:16]


def expected_signature(secret, raw_body):
    return hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()


def signature_matches(secret, raw_body, provided):
    return expected_signature(secret, raw_body) == provided


def constant_time_matches(a, b):
    return hmac.compare_digest(a, b)
