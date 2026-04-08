from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from app.database.connection import SessionLocal
from app.database import models

load_dotenv()

router = APIRouter()

# JWT CONFIG
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200

# SECURITY
security = HTTPBearer()

# PASSWORD HASHING
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password[:72])

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Token missing email")

        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.email == email).first()
        finally:
            db.close()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found in DB")

        return user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


# REQUEST MODELS
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ROUTES
@router.post("/register")
def register(user: UserCreate):
    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")

        new_user = models.User(
            name=user.name,
            email=user.email,
            password=hash_password(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "Registered successfully"}
    finally:
        db.close()


@router.post("/login")
def login(user: UserLogin):
    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.email == user.email).first()

        if not existing:
            raise HTTPException(status_code=400, detail="User not registered")

        if not verify_password(user.password, existing.password):
            raise HTTPException(status_code=400, detail="Wrong password")

        token = create_access_token({"sub": existing.email})

        return {
            "access_token": token,
            "token_type": "bearer"
        }
    finally:
        db.close()


@router.get("/profile")
def profile(current_user=Depends(get_current_user)):
    return {
        "message": "SUCCESS",
        "name": current_user.name,
        "email": current_user.email
    }