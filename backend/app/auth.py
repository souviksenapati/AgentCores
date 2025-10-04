"""
Authentication and authorization module for AgentCores
Provides JWT token handling, password verification, and role-based access control
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_org_db
from app.models.database import User, UserRole

# Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Password hashing with fallback
def _simple_hash_password(password: str, salt: bytes = None) -> str:
    if salt is None:
        salt = secrets.token_bytes(32)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt.hex() + ":" + pwd_hash.hex()


def _simple_verify_password(password: str, hash_str: str) -> bool:
    try:
        salt_hex, hash_hex = hash_str.split(":")
        salt = bytes.fromhex(salt_hex)
        expected_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 100000
        )
        return expected_hash.hex() == hash_hex
    except:
        return False


try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    USE_BCRYPT = True
except:
    USE_BCRYPT = False

security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if USE_BCRYPT:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except:
            return _simple_verify_password(plain_password, hashed_password)
    else:
        return _simple_verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    if USE_BCRYPT:
        try:
            return pwd_context.hash(password)
        except:
            return _simple_hash_password(password)
    else:
        return _simple_hash_password(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if (
        not user
        or not verify_password(password, user.password_hash)
        or not user.is_active
    ):
        return None
    return user


async def get_current_user_from_token(token: str, db: Session) -> Optional[User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return None

    user.last_activity = datetime.utcnow()
    db.commit()
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_org_db),
) -> User:
    user = await get_current_user_from_token(credentials.credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_tenant_id(current_user: User = Depends(get_current_user)) -> str:
    return current_user.tenant_id


def require_admin_or_member_role(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Member role or higher required",
        )
    return current_user


def get_db():
    db = next(get_org_db())
    try:
        yield db
    finally:
        db.close()
