import sqlite3
import json
from vault.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS config (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        salt BLOB NOT NULL,
        kdf_params TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        stored_path TEXT NOT NULL,
        nonce BLOB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        filename TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def vault_exists():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM config WHERE id = 1")
    count = cur.fetchone()[0]
    conn.close()
    return count > 0

def save_config(salt: bytes, kdf_params: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM config WHERE id = 1")
    cur.execute(
        "INSERT INTO config (id, salt, kdf_params) VALUES (1, ?, ?)",
        (salt, json.dumps(kdf_params)),
    )
    conn.commit()
    conn.close()

def load_config():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT salt, kdf_params FROM config WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row["salt"], json.loads(row["kdf_params"])

def add_file_record(filename, stored_path, nonce):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO files (filename, stored_path, nonce) VALUES (?, ?, ?)",
        (filename, stored_path, nonce),
    )
    file_id = cur.lastrowid
    conn.commit()
    conn.close()
    return file_id

def list_files():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM files ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_file(filename):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM files WHERE filename = ?", (filename,))
    row = cur.fetchone()
    conn.close()
    return row

def remove_file_record(filename):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM files WHERE filename = ?", (filename,))
    conn.commit()
    conn.close()

def log_action(action, filename=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (action, filename) VALUES (?, ?)",
        (action, filename),
    )
    conn.commit()
    conn.close()

def get_logs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows