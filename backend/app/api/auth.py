from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, decode_token
from app.schemas.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def _format_user(user_doc: dict) -> dict:
    """Convert MongoDB document to UserResponse-compatible dict."""
    return {
        "id": str(user_doc["_id"]),
        "name": user_doc["name"],
        "email": user_doc["email"],
        "role": user_doc.get("role", "student"),
        "created_at": user_doc.get("created_at", datetime.datetime.utcnow()),
    }


async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return user_doc


async def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


@router.post("/register", response_model=TokenResponse)
async def register_user(user_in: UserRegister, db=Depends(get_db)):
    existing = await db["users"].find_one({"email": user_in.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    role = user_in.role if user_in.role in ["student", "admin"] else "student"
    hashed_pw = get_password_hash(user_in.password)

    new_user = {
        "name": user_in.name,
        "email": user_in.email.lower(),
        "password_hash": hashed_pw,
        "role": role,
        "created_at": datetime.datetime.utcnow(),
    }
    result = await db["users"].insert_one(new_user)
    new_user["_id"] = result.inserted_id

    token = create_access_token(subject=str(result.inserted_id), role=role)
    return TokenResponse(access_token=token, token_type="bearer", user=UserResponse(**_format_user(new_user)))


@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin, db=Depends(get_db)):
    user_doc = await db["users"].find_one({"email": credentials.email.lower()})
    if not user_doc or not verify_password(credentials.password, user_doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(subject=str(user_doc["_id"]), role=user_doc.get("role", "student"))
    return TokenResponse(access_token=token, token_type="bearer", user=UserResponse(**_format_user(user_doc)))


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user_doc = await db["users"].find_one({"email": form_data.username.lower()})
    if not user_doc or not verify_password(form_data.password, user_doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(subject=str(user_doc["_id"]), role=user_doc.get("role", "student"))
    return TokenResponse(access_token=token, token_type="bearer", user=UserResponse(**_format_user(user_doc)))


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return UserResponse(**_format_user(current_user))
