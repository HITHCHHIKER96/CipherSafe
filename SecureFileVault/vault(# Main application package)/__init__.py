"""Secure File Vault - Password-based encrypted file storage."""

__version__ = "0.1.0"

from vault.crypto_utils import derive_key, encrypt_file, decrypt_file
from vault.db import init_database, get_connection
from vault.auth import init_vault, open_vault
from vault.file_manager import add_file, remove_file, list_files, decrypt_file, search_files
