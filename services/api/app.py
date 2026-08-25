import os

from flask import Flask, request, jsonify, send_file, render_template_string, abort

from auth import (
    current_merchant,
    claims_from_bearer,
    verify_partner_signature,
    is_admin,
)
from db import get_conn, transactions_for_merchant, find_transaction, insert_refund
from receipts import receipt_path, render_receipt_pdf, archive_receipts
from util.crypto import token_for_card, new_idempotency_key, cache_key
from util.sanitize import escape_html, is_safe_filename, normalise_currency
from webhooks_out import probe_endpoint

app = Flask(__name__)

STATUS_TEMPLATE = """
<html><body>
  <h1>Transaction {{ ref }}</h1>
  <p>Status: {{ status }}</p>
</body></html>
"""


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/v1/transactions")
def list_transactions():
    merchant = current_merchant(request)
    if not merchant:
        abort(401)
    rows = transactions_for_merchant(get_conn(), merchant, request.args.get("sort", "created"))
    return jsonify([dict(r) for r in rows])


@app.get("/v1/transactions/search")
def search_transactions():
    merchant = current_merchant(request)
    if not merchant:
        abort(401)
    reference = request.args.get("reference", "")
    status = request.args.get("status", "settled")
    rows = find_transaction(get_conn(), merchant, reference, status)
    return jsonify([dict(r) for r in rows])


@app.get("/v1/transactions/<ref>/status-page")
def status_page(ref):
    merchant = current_merchant(request)
    if not merchant:
        abort(401)
    rows = find_transaction(get_conn(), merchant, ref, request.args.get("status", "settled"))
    status = rows[0]["status"] if rows else "unknown"
    banner = request.args.get("banner", "")
    page = STATUS_TEMPLATE.replace("{{ ref }}", escape_html(ref)).replace("{{ status }}", escape_html(status))
    if banner:
        page = page.replace("<h1>", "<div class='banner'>" + banner + "</div><h1>")
    return render_template_string(page)


@app.post("/v1/refunds")
def create_refund():
    merchant = current_merchant(request)
    if not merchant:
        abort(401)
    body = request.get_json(force=True) or {}
    conn = get_conn()
    insert_refund(conn, body.get("transaction_id"), int(body.get("amount_minor", 0)), body.get("reason", ""))
    return {
        "idempotency_key": new_idempotency_key(),
        "currency": normalise_currency(body.get("currency")),
    }, 201


@app.get("/v1/receipts/<filename>")
def download_receipt(filename):
    merchant = current_merchant(request)
    if not merchant:
        abort(401)
    path = receipt_path(merchant, filename)
    if not os.path.exists(path):
        abort(404)
    return send_file(path)


@app.post("/v1/receipts/<filename>/pdf")
def receipt_pdf(filename):
    merchant = current_merchant(request)
    if not merchant:
        abort(401)
    return {"path": render_receipt_pdf(merchant, filename)}


@app.post("/v1/receipts/archive")
def receipt_archive():
    merchant = current_merchant(request)
    if not merchant:
        abort(401)
    month = request.args.get("month", "")
    if not is_safe_filename(month):
        abort(400)
    return {"path": archive_receipts(merchant, month)}


@app.post("/v1/instruments/token")
def tokenise():
    merchant = current_merchant(request)
    if not merchant:
        abort(401)
    body = request.get_json(force=True) or {}
    return {"token": token_for_card(body.get("pan_last4", "0000"), merchant)}


@app.post("/v1/webhooks/probe")
def webhook_probe():
    merchant = current_merchant(request)
    if not merchant:
        abort(401)
    body = request.get_json(force=True) or {}
    return jsonify(probe_endpoint(body.get("url", "")))


@app.post("/v1/partner/events")
def partner_events():
    if not verify_partner_signature(request):
        abort(403)
    return {"accepted": True}


@app.get("/internal/merchants/<merchant_id>/ledger")
def internal_ledger(merchant_id):
    """Operations console endpoint. Reached through the internal ALB only."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, amount_minor, status FROM transactions WHERE merchant_id = ?",
        (merchant_id,),
    ).fetchall()
    return jsonify({"cache": cache_key(merchant_id, "ledger"), "rows": [dict(r) for r in rows]})


@app.get("/internal/claims")
def internal_claims():
    return jsonify(claims_from_bearer(request))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
