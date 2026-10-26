"""
Unit tests for backend.app.core.security.
Tests secure password hashing (bcrypt and scrypt KDF) and rejection of insecure downgrades (Addresses Finding P0).
"""
import hashlib
import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    _scrypt_hash,
    SCRYPT_N,
    SCRYPT_R,
    SCRYPT_P
)


def test_password_hash_and_verify_success():
    password = "MiningSafety2026!#"
    hashed = get_password_hash(password)
    assert isinstance(hashed, str)
    assert hashed.startswith(("$2b$", "$scrypt$"))
    assert verify_password(password, hashed) is True


def test_password_verify_wrong_password():
    password = "MiningSafety2026!#"
    wrong_password = "WrongPassword123"
    hashed = get_password_hash(password)
    assert verify_password(wrong_password, hashed) is False


def test_rejection_of_plain_sha256_downgrade():
    """Verify that insecure plain SHA-256 hashes are strictly rejected."""
    password = "MySecretPassword"
    plain_sha256 = hashlib.sha256(password.encode("utf-8")).hexdigest()
    
    # Must NOT verify, preventing silent downgrade attacks
    assert verify_password(password, plain_sha256) is False


def test_rejection_of_malformed_hashes():
    password = "MySecretPassword"
    assert verify_password(password, "") is False
    assert verify_password(password, "$scrypt$invalid$format") is False
    assert verify_password(password, "$2b$invalid_bcrypt_hash") is False
    assert verify_password(None, "some_hash") is False
    assert verify_password(password, None) is False


def test_scrypt_explicit_verification():
    """Directly tests scrypt verification format."""
    import secrets
    password = "OperatorKey_Underground"
    salt = secrets.token_bytes(16)
    hash_bytes = _scrypt_hash(password.encode("utf-8"), salt)
    scrypt_formatted = f"$scrypt$n={SCRYPT_N},r={SCRYPT_R},p={SCRYPT_P}${salt.hex()}${hash_bytes.hex()}"
    
    assert verify_password(password, scrypt_formatted) is True
    assert verify_password("WrongKey", scrypt_formatted) is False
