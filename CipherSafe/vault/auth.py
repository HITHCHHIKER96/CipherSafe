import os
import getpass
from vault import crypto_utils, db
from vault.config import SALT_SIZE, KDF_ITERATIONS, KDF_MEMORY_KIB, KDF_PARALLELISM

def init_vault():
    db.init_database()

    print("Initialize vault")
    p1 = getpass.getpass("Set master password: ")
    p2 = getpass.getpass("Confirm master password: ")

    if p1 != p2:
        raise ValueError("Passwords do not match")

    salt = os.urandom(SALT_SIZE)
    key = crypto_utils.derive_key(p1, salt)

    db.save_config(
        salt,
        {
            "iterations": KDF_ITERATIONS,
            "memory_kib": KDF_MEMORY_KIB,
            "parallelism": KDF_PARALLELISM,
        },
    )
    print("Vault initialized successfully.")
    return key

def open_vault():
    config = db.load_config()
    if not config:
        raise ValueError("Vault not initialized. Run init first.")

    salt, _ = config
    pwd = getpass.getpass("Enter master password: ")
    key = crypto_utils.derive_key(pwd, salt)
    print("Vault unlocked.")
    return key