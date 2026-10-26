try:
    import bcrypt
except ImportError:
    bcrypt = None

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import hashlib
import secrets

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

SCRYPT_N = 16384
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_KEY_LEN = 32


def _scrypt_hash(password_bytes: bytes, salt_bytes: bytes) -> bytes:
    """Computes memory-hard scrypt KDF (NIST/OWASP recommended)."""
    return hashlib.scrypt(
        password_bytes,
        salt=salt_bytes,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_KEY_LEN
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against a bcrypt or scrypt hash. Rejects insecure plain hashes."""
    if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
        return False
    
    plain_bytes = plain_password.encode('utf-8')
    
    # 1. Bcrypt Hash Format ($2b$ or $2a$)
    if hashed_password.startswith(("$2b$", "$2a$", "$2y$")):
        if bcrypt is not None:
            try:
                return bcrypt.checkpw(plain_bytes, hashed_password.encode('utf-8'))
            except Exception:
                return False
        else:
            # Cannot safely verify a bcrypt hash without the bcrypt algorithm
            return False
            
    # 2. Scrypt Hash Format ($scrypt$n=16384,r=8,p=1$<salt_hex>$<hash_hex>)
    if hashed_password.startswith("$scrypt$"):
        try:
            parts = hashed_password.split("$")
            # Expected format: ['', 'scrypt', 'params', 'salt_hex', 'hash_hex']
            if len(parts) != 5:
                return False
            salt = bytes.fromhex(parts[3])
            expected_hash = bytes.fromhex(parts[4])
            computed_hash = _scrypt_hash(plain_bytes, salt)
            return secrets.compare_digest(computed_hash, expected_hash)
        except Exception:
            return False

    # 3. Explicitly reject any insecure downgrade (e.g. plain sha256 or md5)
    return False


def get_password_hash(password: str) -> str:
    """Generates a secure password hash using bcrypt if available, or scrypt KDF with random salt."""
    if not isinstance(password, str):
        raise TypeError("Password must be a string")
        
    password_bytes = password.encode('utf-8')
    
    if bcrypt is not None:
        return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    # Cryptographically secure scrypt KDF fallback using Python standard library
    salt = secrets.token_bytes(16)
    hash_bytes = _scrypt_hash(password_bytes, salt)
    return f"$scrypt$n={SCRYPT_N},r={SCRYPT_R},p={SCRYPT_P}${salt.hex()}${hash_bytes.hex()}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Re-export get_current_user from deps to allow importing from either location
def get_current_user():
    from app.api.deps import get_current_user as _get_current_user
    return _get_current_user

# For use as Depends()
from app.api.deps import get_current_user
