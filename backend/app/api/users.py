from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from datetime import datetime, timedelta

from app.database.connection import SessionLocal
from app.database import models

router = APIRouter()

# =========================
# JWT CONFIG
# =========================
SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # increased to 60 mins

# =========================
# SECURITY
# =========================
security = HTTPBearer()

# =========================
# PASSWORD HASHING
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password[:72])

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# =========================
# TOKEN CREATION
# =========================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("✅ TOKEN CREATED:", token)
    return token

# =========================
# GET CURRENT USER
# =========================
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    print("🔥 get_current_user CALLED")  # this MUST print if token is being sent
    try:
        token = credentials.credentials
        print("📨 TOKEN RECEIVED:", token)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("📦 PAYLOAD:", payload)

        email = payload.get("sub")
        print("📧 EMAIL FROM TOKEN:", email)

        if email is None:
            raise HTTPException(status_code=401, detail="Token missing email")

        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.email == email).first()
        finally:
            db.close()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found in DB")

        print("✅ AUTH SUCCESS for:", email)
        return user

    except JWTError as e:
        print("❌ JWT ERROR:", str(e))
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")

    except HTTPException:
        raise  # re-raise HTTP exceptions as-is

    except Exception as e:
        print("❌ GENERAL ERROR:", str(e))
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


# =========================
# REQUEST MODELS
# =========================
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# =========================
# ROUTES
# =========================

@router.post("/register")
def register(user: UserCreate):
    db = SessionLocal()
    try:
        print("📝 REGISTERING USER:", user.email)

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

        print("✅ USER REGISTERED:", user.email)
        return {"message": "Registered successfully"}

    finally:
        db.close()


@router.post("/login")
def login(user: UserLogin):
    db = SessionLocal()
    try:
        print("🔐 LOGIN ATTEMPT:", user.email)

        existing = db.query(models.User).filter(models.User.email == user.email).first()

        if not existing:
            raise HTTPException(status_code=400, detail="User not registered")

        if not verify_password(user.password, existing.password):
            raise HTTPException(status_code=400, detail="Wrong password")

        token = create_access_token({"sub": existing.email})

        print("✅ LOGIN SUCCESS:", user.email)
        return {
            "access_token": token,
            "token_type": "bearer"
        }

    finally:
        db.close()


@router.get("/profile")
def profile(current_user=Depends(get_current_user)):
    return {
        "message": "SUCCESS ✅",
        "name": current_user.name,
        "email": current_user.email
    }


# =========================
# TEST ROUTE (remove later)
# =========================
@router.get("/test-token")
def test_token():
    """Use this to verify JWT is working correctly"""
    token = create_access_token({"sub": "test@test.com"})
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"status": "JWT working ✅", "token": token, "decoded": decoded}
    except JWTError as e:
        return {"status": "JWT broken ❌", "error": str(e)}