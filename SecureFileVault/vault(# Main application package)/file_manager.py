# File operations

"""High-level Vault operations (add, remove, list, decrypt files)."""

import os
import uuid
from pathlib import Path
from vault import crypto_utils, db
from vault.config import VAULT_FILES_DIR


def add_file(filepath: str, key: bytes) -> int:
    """
    Encrypt a file and add it to the vault.
    
    Args:
        filepath: Path to plaintext file
        key: 32-byte AES key
    
    Returns:
        File ID in database
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    
    # Generate unique stored path
    unique_id = uuid.uuid4().hex
    stored_filename = f"{unique_id}.enc"
    stored_path = str(VAULT_FILES_DIR / stored_filename)
    
    # Encrypt file
    nonce, tag = crypto_utils.encrypt_file(filepath, stored_path, key)
    
    # Add to database
    file_id = db.add_file_record(filename, stored_path, nonce, tag, filesize)
    
    # Log action
    db.log_action('ENCRYPT', file_id, user='SYSTEM')
    
    return file_id


def remove_file(filename: str, key: bytes) -> None:
    """
    Remove a file from the vault (delete encrypted file + DB entry).
    
    Args:
        filename: Original filename to remove
        key: 32-byte AES key (for verification)
    """
    file_record = db.get_file_record_by_name(filename)
    
    if file_record is None:
        raise ValueError(f"File not found in vault: {filename}")
    
    file_id = file_record['id']
    stored_path = file_record['stored_path']
    
    # Delete encrypted file from disk
    if os.path.exists(stored_path):
        os.remove(stored_path)
    
    # Delete from database
    db.remove_file_record(file_id)
    
    # Log action
    db.log_action('DELETE', file_id, user='SYSTEM')


def list_files() -> list[dict]:
    """List all files in the vault."""
    return db.list_all_files()


def search_files(keyword: str) -> list[dict]:
    """Search files by filename."""
    return db.search_files(keyword)


def decrypt_file(filename: str, key: bytes, output_dir: str = None) -> str:
    """
    Decrypt a file from the vault.
    
    Args:
        filename: Original filename to decrypt
        key: 32-byte AES key
        output_dir: Where to write decrypted file (default: current dir)
    
    Returns:
        Path to decrypted file
    """
    file_record = db.get_file_record_by_name(filename)
    
    if file_record is None:
        raise ValueError(f"File not found in vault: {filename}")
    
    stored_path = file_record['stored_path']
    nonce = file_record['nonce']
    tag = file_record['tag']
    
    # Determine output path
    if output_dir is None:
        output_dir = os.getcwd()
    
    output_path = os.path.join(output_dir, filename)
    
    # Decrypt
    crypto_utils.decrypt_file(stored_path, output_path, key, nonce, tag)
    
    # Update timestamp
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE files SET modified_at = CURRENT_TIMESTAMP WHERE id = ?",
        (file_record['id'],)
    )
    conn.commit()
    conn.close()
    
    # Log action
    db.log_action('DECRYPT', file_record['id'], user='SYSTEM')
    
    return output_path


def get_file_info(filename: str) -> dict | None:
    """Get detailed info about a file in the vault."""
    return db.get_file_record_by_name(filename)
