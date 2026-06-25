import os
import uuid
from vault import crypto_utils, db
from vault.config import VAULT_FILES_DIR

def add_file(filepath, key):
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)

    filename = os.path.basename(filepath)
    stored_name = f"{uuid.uuid4().hex}.enc"
    stored_path = str(VAULT_FILES_DIR / stored_name)

    nonce, _ = crypto_utils.encrypt_file(filepath, stored_path, key)
    db.add_file_record(filename, stored_path, nonce)
    db.log_action("ENCRYPT", filename)
    return filename

def decrypt_file(filename, key, output_dir="."):
    row = db.get_file(filename)
    if not row:
        raise ValueError("File not found in vault")

    out_path = os.path.join(output_dir, filename)
    crypto_utils.decrypt_file(row["stored_path"], out_path, key, row["nonce"])
    db.log_action("DECRYPT", filename)
    return out_path

def remove_file(filename):
    row = db.get_file(filename)
    if not row:
        raise ValueError("File not found in vault")

    if os.path.exists(row["stored_path"]):
        os.remove(row["stored_path"])
    db.remove_file_record(filename)
    db.log_action("DELETE", filename)

def list_files():
    return db.list_files()

def search_files(keyword):
    files = db.list_files()
    return [f for f in files if keyword.lower() in f["filename"].lower()]