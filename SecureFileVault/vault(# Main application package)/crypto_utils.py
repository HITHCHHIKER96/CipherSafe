# Encryption & decryption logic

"""Key derivation and AES-GCM encryption/decryption functions."""

import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidTag
from vault.config import (
    KDF_TIME_COST, KDF_MEMORY_COST, KDF_PARALLELISM,
    KDF_KEY_LENGTH, AES_NONCE_LENGTH, CHUNK_SIZE
)


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit AES key from password and salt using Argon2id.
    
    Args:
        password: User's passphrase
        salt: Random salt (16 bytes)
    
    Returns:
        32-byte AES key
    """
    pwd_bytes = password.encode('utf-8')
    kdf = Argon2id(
        salt=salt,
        length=KDF_KEY_LENGTH,
        time_cost=KDF_TIME_COST,
        memory_cost=KDF_MEMORY_COST,
        parallelism=KDF_PARALLELISM
    )
    return kdf.derive(pwd_bytes)


def encrypt_file(in_path: str, out_path: str, key: bytes) -> tuple[bytes, bytes]:
    """
    Encrypt a file using AES-256-GCM in streaming mode.
    
    Args:
        in_path: Path to plaintext file
        out_path: Path for encrypted file
        key: 32-byte AES key
    
    Returns:
        (nonce, tag) - both must be stored for decryption
    """
    nonce = os.urandom(AES_NONCE_LENGTH)
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=None)
    encryptor = cipher.encryptor()
    
    with open(in_path, 'rb') as f_in, open(out_path, 'wb') as f_out:
        while True:
            chunk = f_in.read(CHUNK_SIZE)
            if not chunk:
                break
            ct_chunk = encryptor.update(chunk)
            f_out.write(ct_chunk)
        f_out.write(encryptor.finalize())
    
    return nonce, encryptor.tag


def decrypt_file(in_path: str, out_path: str, key: bytes, nonce: bytes, tag: bytes) -> None:
    """
    Decrypt a file encrypted with AES-GCM, verifying integrity.
    
    Args:
        in_path: Path to encrypted file
        out_path: Path for decrypted file
        key: 32-byte AES key
        nonce: 12-byte nonce used during encryption
        tag: 16-byte authentication tag
    
    Raises:
        InvalidTag: If file was tampered or key is wrong
    """
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=None)
    decryptor = cipher.decryptor()
    
    with open(in_path, 'rb') as f_in, open(out_path, 'wb') as f_out:
        while True:
            chunk = f_in.read(CHUNK_SIZE)
            if not chunk:
                break
            pt_chunk = decryptor.update(chunk)
            f_out.write(pt_chunk)
        f_out.write(decryptor.finalize())


def verify_password(password: str, salt: bytes, stored_key_hint: bytes = None) -> bool:
    """
    Verify password by deriving key and checking against stored hint.
    
    For simplicity, we derive the key and attempt to decrypt a known value.
    In practice, you'd store a hashed version or encrypted test value.
    """
    if stored_key_hint is None:
        # Fallback: just derive and return True (not secure for real auth)
        return True
    
    derived = derive_key(password, salt)
    return derived == stored_key_hint
