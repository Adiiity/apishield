import os
import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from database import SessionLocal, User, RoleEnum
from sqlalchemy.orm import Session

load_dotenv()

# Secret Key (stored in .env file)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Hash password
def hash_password(password):
    return pwd_context.hash(password)

# Create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    if "sub" not in to_encode:
        raise ValueError("Token must include a 'sub' field")
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get database session
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username : str, password: str, role: str = "user"):
    if role not in RoleEnum.__members__:
        raise HTTPException(status_code=400, detail="Invalid role")
    hashed_pw=hash_password(password)
    user= User(username=username, hashed_password=hashed_pw, role=RoleEnum[role])
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if not isinstance(payload, dict):
            raise HTTPException(status_code=401, detail="Invalid token format")

        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token: 'sub' missing")

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")