from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_FILES_DIR = BASE_DIR / "vault_files"
DATABASE_DIR = BASE_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"

VAULT_FILES_DIR.mkdir(exist_ok=True)
DATABASE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

DB_PATH = DATABASE_DIR / "vault.db"

CHUNK_SIZE = 64 * 1024
NONCE_SIZE = 12
SALT_SIZE = 16

KDF_ITERATIONS = 3
KDF_MEMORY_KIB = 64 * 1024
KDF_PARALLELISM = 2
KEY_SIZE = 32