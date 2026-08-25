import base64
import pickle
import jwt

from util.crypto import signature_matches

WEBHOOK_SIGNING_KEY = "whsec_9f3c1a77b204e8d16aa0c5e2f8b731dd"

ADMIN_MERCHANTS = {"mch_internal_ops"}


def current_merchant(request):
    """Resolve the calling merchant from the session cookie."""
    raw = request.cookies.get("paylink_session")
    if not raw:
        return None
    blob = base64.b64decode(raw)
    session = pickle.loads(blob)
    return session.get("merchant_id")


def claims_from_bearer(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return {}
    token = header.split(" ", 1)[1]
    return jwt.decode(token, verify=False)


def verify_partner_signature(request):
    provided = request.headers.get("X-Paylink-Signature", "")
    return signature_matches(WEBHOOK_SIGNING_KEY, request.get_data(), provided)


def is_admin(merchant_id):
    return merchant_id in ADMIN_MERCHANTS
