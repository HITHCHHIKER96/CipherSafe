# SQLite database functions

"""SQLite database setup and metadata schema."""

import sqlite3
from pathlib import Path
from vault.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """Create all tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Config table (stores salt and KDF params)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY,
            salt BLOB NOT NULL,
            kdf_params TEXT NOT NULL
        )
    ''')
    
    # Files table (metadata for encrypted files)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            nonce BLOB NOT NULL,
            tag BLOB NOT NULL,
            filesize INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Logs table (activity tracking)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            action TEXT NOT NULL,
            file_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user TEXT,
            FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()


def store_vault_config(salt: bytes, kdf_params: dict) -> None:
    """Store vault initialization config (salt + KDF params)."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Delete existing config if any
    cur.execute("DELETE FROM config")
    
    cur.execute(
        "INSERT INTO config (id, salt, kdf_params) VALUES (1, ?, ?)",
        (salt, str(kdf_params))
    )
    
    conn.commit()
    conn.close()


def get_vault_config() -> tuple[bytes, dict]:
    """Retrieve vault config (salt and KDF params)."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT salt, kdf_params FROM config WHERE id = 1")
    row = cur.fetchone()
    
    conn.close()
    
    if row is None:
        raise ValueError("Vault not initialized")
    
    salt = row[0]
    kdf_params = eval(row[1])  # Simple parsing; use json in production
    
    return salt, kdf_params


def add_file_record(filename: str, stored_path: str, nonce: bytes, tag: bytes, filesize: int) -> int:
    """Insert a new file record and return its ID."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        """INSERT INTO files (filename, stored_path, nonce, tag, filesize) 
           VALUES (?, ?, ?, ?, ?)""",
        (filename, stored_path, nonce, tag, filesize)
    )
    
    file_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return file_id


def get_file_record(file_id: int) -> dict | None:
    """Get file record by ID."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM files WHERE id = ?", (file_id,))
    row = cur.fetchone()
    
    conn.close()
    
    if row is None:
        return None
    
    return {
        'id': row[0],
        'filename': row[1],
        'stored_path': row[2],
        'nonce': row[3],
        'tag': row[4],
        'filesize': row[5],
        'created_at': row[6],
        'modified_at': row[7]
    }


def get_file_record_by_name(filename: str) -> dict | None:
    """Get file record by filename."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM files WHERE filename = ?", (filename,))
    row = cur.fetchone()
    
    conn.close()
    
    if row is None:
        return None
    
    return {
        'id': row[0],
        'filename': row[1],
        'stored_path': row[2],
        'nonce': row[3],
        'tag': row[4],
        'filesize': row[5],
        'created_at': row[6],
        'modified_at': row[7]
    }


def list_all_files() -> list[dict]:
    """Get all file records."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM files ORDER BY created_at DESC")
    rows = cur.fetchall()
    
    conn.close()
    
    return [
        {
            'id': row[0],
            'filename': row[1],
            'stored_path': row[2],
            'nonce': row[3],
            'tag': row[4],
            'filesize': row[5],
            'created_at': row[6],
            'modified_at': row[7]
        }
        for row in rows
    ]


def search_files(keyword: str) -> list[dict]:
    """Search files by filename containing keyword."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT * FROM files WHERE filename LIKE ? ORDER BY created_at DESC",
        (f"%{keyword}%",)
    )
    rows = cur.fetchall()
    
    conn.close()
    
    return [
        {
            'id': row[0],
            'filename': row[1],
            'stored_path': row[2],
            'nonce': row[3],
            'tag': row[4],
            'filesize': row[5],
            'created_at': row[6],
            'modified_at': row[7]
        }
        for row in rows
    ]


def remove_file_record(file_id: int) -> None:
    """Delete file record by ID."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM files WHERE id = ?", (file_id,))
    
    conn.commit()
    conn.close()


def log_action(action: str, file_id: int = None, user: str = None) -> None:
    """Log an action to the logs table."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "INSERT INTO logs (action, file_id, user) VALUES (?, ?, ?)",
        (action, file_id, user)
    )
    
    conn.commit()
    conn.close()


def get_logs(limit: int = 50) -> list[dict]:
    """Get recent logs."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    
    conn.close()
    
    return [
        {
            'id': row[0],
            'action': row[1],
            'file_id': row[2],
            'timestamp': row[3],
            'user': row[4]
        }
        for row in rows
    ]
