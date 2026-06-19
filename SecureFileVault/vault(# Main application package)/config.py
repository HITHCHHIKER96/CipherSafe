# Configuration settings

"""Configuration constants for the vault."""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_FILES_DIR = BASE_DIR / "vault_files"
DATABASE_DIR = BASE_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure directories exist
VAULT_FILES_DIR.mkdir(exist_ok=True)
DATABASE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Database path
DB_PATH = DATABASE_DIR / "vault.db"

# KDF (Argon2id) parameters
KDF_TIME_COST = 3          # Iterations
KDF_MEMORY_COST = 64 * 1024  # 64 MiB (in KiB)
KDF_PARALLELISM = 4        # Threads
KDF_KEY_LENGTH = 32        # 256 bits (AES-256)

# Encryption parameters
AES_KEY_LENGTH = 32        # 256 bits
AES_NONCE_LENGTH = 12      # 96 bits (GCM)
AES_TAG_LENGTH = 16        # 128 bits (authentication tag)

# Chunk size for streaming (64 KB)
CHUNK_SIZE = 64 * 1024

# Log file path
LOG_FILE = LOGS_DIR / "activity.log"
