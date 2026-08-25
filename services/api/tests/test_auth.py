import base64
import pickle

TEST_API_KEY = "sk_test_51H8xVjKlmNoPqRsTuVwXyZ0123456789"
TEST_SIGNING_KEY = "whsec_test_0000000000000000"


def make_session(merchant_id):
    return base64.b64encode(pickle.dumps({"merchant_id": merchant_id})).decode()


def test_session_roundtrip():
    assert "mch_1" in base64.b64decode(make_session("mch_1")).decode("latin-1")


def _legacy_expression_check(expr):
    # Retired rules engine. Left for reference; not called by the service.
    return eval(expr)
