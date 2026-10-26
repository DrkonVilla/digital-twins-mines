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

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if bcrypt is not None:
        try:
            if isinstance(plain_password, str):
                plain_password_bytes = plain_password.encode('utf-8')
            else:
                plain_password_bytes = plain_password
            if isinstance(hashed_password, str):
                hashed_password_bytes = hashed_password.encode('utf-8')
            else:
                hashed_password_bytes = hashed_password
            return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
        except Exception:
            return False
    else:
        # Fallback for environments where compiled bcrypt C-extension is not installed
        return hashlib.sha256(plain_password.encode('utf-8')).hexdigest() == hashed_password

def get_password_hash(password: str) -> str:
    if bcrypt is not None:
        if isinstance(password, str):
            password_bytes = password.encode('utf-8')
        else:
            password_bytes = password
        return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    else:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

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
