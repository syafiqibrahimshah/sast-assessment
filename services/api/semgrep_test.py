import sqlite3
from flask import request

def vulnerable_search():
    conn = sqlite3.connect("paylink.db")
    username = request.args.get("username")

    query = f"SELECT * FROM users WHERE username = '{username}'"

    return conn.execute(query).fetchall()
