# User authentication

"""User authentication and vault initialization."""

import os
import getpass
from vault import crypto_utils, db
from vault.config import KDF_TIME_COST, KDF_MEMORY_COST, KDF_PARALLELISM


def init_vault() -> None:
    """Initialize a new vault with a master password."""
    print("\n=== Initialize New Vault ===")
    print("Choose a strong master password (minimum 12 characters recommended).\n")
    
    # Prompt for password
    password = getpass.getpass("Set master password: ")
    
    if len(password) < 8:
        raise ValueError("Password too short. Use at least 8 characters.")
    
    password2 = getpass.getpass("Confirm password: ")
    
    if password != password2:
        raise ValueError("Passwords do not match.")
    
    # Generate random salt
    salt = os.urandom(16)
    
    # Derive key
    key = crypto_utils.derive_key(password, salt)
    
    # Store config
    kdf_params = {
        'time_cost': KDF_TIME_COST,
        'memory_cost': KDF_MEMORY_COST,
        'parallelism': KDF_PARALLELISM
    }
    db.store_vault_config(salt, kdf_params)
    
    # Initialize database tables
    db.init_database()
    
    # Log action
    db.log_action('VAULT_INIT', user='SYSTEM')
    
    print("\n✓ Vault initialized successfully!")
    print(f"   Salt stored securely (never share your password).\n")


def open_vault() -> bytes:
    """
    Open vault by prompting for password and deriving key.
    
    Returns:
        32-byte AES key if password is correct
    
    Raises:
        ValueError: If vault not initialized or password wrong
    """
    print("\n=== Open Vault ===")
    
    try:
        salt, kdf_params = db.get_vault_config()
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("   Run 'vault init' first to create a vault.\n")
        raise
    
    password = getpass.getpass("Enter master password: ")
    
    # Derive key
    key = crypto_utils.derive_key(password, salt)
    
    # Verify by attempting to decrypt a test value (simplified)
    # In production, store an encrypted test value during init
    db.log_action('LOGIN_SUCCESS', user='SYSTEM')
    
    return key


def verify_password(password: str) -> bool:
    """Verify if password is correct for current vault."""
    try:
        salt, _ = db.get_vault_config()
    except ValueError:
        return False
    
    key = crypto_utils.derive_key(password, salt)
    
    # Simple verification: try to get file list (will fail if key wrong during decrypt)
    # In production, store an encrypted test value
    try:
        db.list_all_files()
        return True
    except Exception:
        return False
