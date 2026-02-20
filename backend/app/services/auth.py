"""
TubeMentor AI - Authentication Service
Handles JWT tokens, password hashing, and Google OAuth
"""

from datetime import datetime, timedelta
from typing import Optional
import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.database import get_db
from app.models.db_models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    return db.query(User).filter(User.google_id == google_id).first()


def create_user(db: Session, email: str, password: str = None, **kwargs) -> User:
    hashed_password = get_password_hash(password) if password else None
    user = User(
        email=email,
        hashed_password=hashed_password,
        **kwargs
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not token:
        return None
    
    payload = decode_token(token)
    if not payload:
        return None
    
    email: str = payload.get("sub")
    if not email:
        return None
    
    user = get_user_by_email(db, email)
    return user


async def get_current_user_required(
    user: User = Depends(get_current_user)
) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def verify_google_token(token: str) -> Optional[dict]:
    """Verify Google OAuth token and return user info."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return None


def create_or_update_google_user(db: Session, google_user_info: dict) -> User:
    """Create or update user from Google OAuth data."""
    google_id = google_user_info.get("sub")
    email = google_user_info.get("email")
    
    # Check if user exists by google_id
    user = get_user_by_google_id(db, google_id)
    if user:
        # Update user info
        user.full_name = google_user_info.get("name")
        user.avatar_url = google_user_info.get("picture")
        db.commit()
        db.refresh(user)
        return user
    
    # Check if user exists by email
    user = get_user_by_email(db, email)
    if user:
        # Link Google account to existing user
        user.google_id = google_id
        user.avatar_url = google_user_info.get("picture", user.avatar_url)
        user.auth_provider = "google"
        db.commit()
        db.refresh(user)
        return user
    
    # Create new user
    return create_user(
        db=db,
        email=email,
        google_id=google_id,
        full_name=google_user_info.get("name"),
        avatar_url=google_user_info.get("picture"),
        auth_provider="google"
    )
