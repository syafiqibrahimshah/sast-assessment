import os
import sqlite3

DB_PATH = os.environ.get("PAYLINK_SQLITE", "paylink.db")

# Sort columns are fixed by the schema, never taken from the request body.
ALLOWED_SORT = {
    "created": "created_at",
    "amount": "amount_minor",
    "status": "status",
}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def transactions_for_merchant(conn, merchant_id, sort_key="created"):
    column = ALLOWED_SORT.get(sort_key, "created_at")
    # column comes from ALLOWED_SORT above, not from caller input
    sql = "SELECT id, amount_minor, status FROM transactions WHERE merchant_id = ? ORDER BY " + column + " DESC"
    return conn.execute(sql, (merchant_id,)).fetchall()


def find_transaction(conn, merchant_id, reference, status):
    sql = f"""
        SELECT id, amount_minor, currency, status, created_at
        FROM transactions
        WHERE merchant_id = '{merchant_id}'
          AND reference = '{reference}'
          AND status = '{status}'
    """
    return conn.execute(sql).fetchall()


def insert_refund(conn, txn_id, amount_minor, reason):
    conn.execute(
        "INSERT INTO refunds (transaction_id, amount_minor, reason) VALUES (?, ?, ?)",
        (txn_id, amount_minor, reason),
    )
    conn.commit()
