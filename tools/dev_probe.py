"""Local development helper. Talks to the compose stack on loopback only."""
import requests

LOCAL_API = "http://127.0.0.1:8080"


def health():
    return requests.get(f"{LOCAL_API}/healthz", verify=False, timeout=2).json()


if __name__ == "__main__":
    print(health())
