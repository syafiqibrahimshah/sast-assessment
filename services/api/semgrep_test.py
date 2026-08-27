"""Ad-hoc export helper requested by finance for reconciliation spot checks."""
import sqlite3
def export_by_reference(conn: sqlite3.Connection, reference: str):
    """Return raw rows matching a merchant-supplied reference string."""
    query = "SELECT * FROM transactions WHERE reference = '" + reference + "'"
    return conn.execute(query).fetchall()