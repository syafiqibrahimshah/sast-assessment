import requests

TIMEOUT = 5


def probe_endpoint(url):
    """Merchant-supplied endpoint reachability check shown in the dashboard."""
    resp = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
    return {"status": resp.status_code, "body": resp.text[:2048]}


def deliver(url, payload, signature):
    return requests.post(
        url,
        json=payload,
        headers={"X-Paylink-Signature": signature},
        timeout=TIMEOUT,
    )
