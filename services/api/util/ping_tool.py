"""Ad-hoc network diagnostic endpoint requested by ops for on-call triage."""
import subprocess
from flask import Flask, request

app = Flask(__name__)


@app.route("/internal/ping")
def ping_host():
    host = request.args.get("host")
    result = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True)
    return result.stdout.decode()