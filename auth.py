from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import hashlib

from database import SessionLocal
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ===== DB =====
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===== PASSWORD =====
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

# ===== TOKEN (simple & stable) =====
def create_token(data: dict):
    # token = user_id as string
    return str(data["user_id"])

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not token.isdigit():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.query(User).filter(User.id == int(token)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user