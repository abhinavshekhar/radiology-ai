"""AES encryption for medical images at rest."""

import base64
import hashlib
from pathlib import Path

from cryptography.fernet import Fernet

from app.config import settings


def _get_fernet() -> Fernet:
    key = hashlib.sha256(settings.secret_key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_file(src: Path) -> Path:
    """Encrypt file in place, returns path with .enc suffix."""
    fernet = _get_fernet()
    data = src.read_bytes()
    encrypted = fernet.encrypt(data)
    enc_path = src.with_suffix(src.suffix + ".enc")
    enc_path.write_bytes(encrypted)
    src.unlink(missing_ok=True)
    return enc_path


def decrypt_file(enc_path: Path) -> bytes:
    fernet = _get_fernet()
    return fernet.decrypt(enc_path.read_bytes())


def decrypt_to_temp(enc_path: Path, temp_dir: Path) -> Path:
    """Decrypt to a temp file for AI processing."""
    base_name = enc_path.name
    if base_name.endswith(".enc"):
        base_name = base_name[:-4]
    out_path = temp_dir / f"tmp_{base_name}"
    out_path.write_bytes(decrypt_file(enc_path))
    return out_path
