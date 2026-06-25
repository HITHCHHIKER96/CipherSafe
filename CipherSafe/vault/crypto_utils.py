import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

from vault.config import (
    CHUNK_SIZE,
    NONCE_SIZE,
    KEY_SIZE,
    KDF_ITERATIONS,
    KDF_MEMORY_KIB,
    KDF_PARALLELISM,
)

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = Argon2id(
        salt=salt,
        length=KEY_SIZE,
        time_cost=KDF_ITERATIONS,
        memory_cost=KDF_MEMORY_KIB,
        parallelism=KDF_PARALLELISM,
    )
    return kdf.derive(password.encode("utf-8"))

def encrypt_file(in_path: str, out_path: str, key: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key)

    with open(in_path, "rb") as f:
        plaintext = f.read()

    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    with open(out_path, "wb") as f:
        f.write(ciphertext)

    tag = ciphertext[-16:]
    return nonce, tag

def decrypt_file(in_path: str, out_path: str, key: bytes, nonce: bytes) -> None:
    aesgcm = AESGCM(key)

    with open(in_path, "rb") as f:
        ciphertext = f.read()

    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    with open(out_path, "wb") as f:
        f.write(plaintext)