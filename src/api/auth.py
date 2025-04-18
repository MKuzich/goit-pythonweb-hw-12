from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.repository.database.db import get_db
from src.repository import users
from src.schemas import UserCreate, UserBase, UserResponse  
from src.services.auth import create_access_token, decode_token, get_current_user, upload_avatar
from src.services.security import  verify_password
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.repository.database.models import User
from src.schemas import RequestPasswordReset, PasswordResetConfirm
from src.services import reset_password
from src.dependencies.roles import require_admin

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=UserBase, status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Sign up a new user.

    :param user: User data
    :param db: SQLAlchemy database session
    :return: Created user
    """
    if users.get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="User already exists")
    return users.create_user(db, user)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Log in a user and return an access token.

    :param form_data: Form data containing username and password
    :param db: SQLAlchemy database session
    :return: Access token and token type
    """
    user = users.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/confirm")
def confirm_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm a user's email address using a token.

    :param token: Confirmation token
    :param db: SQLAlchemy database session
    :return: Confirmation message
    """
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = users.get_user_by_email(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.confirmed = True
    db.commit()
    return {"message": "Email confirmed"}

@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
def read_me(request: Request, current_user = Depends(get_current_user)):
    """
    Get the current user's information.

    :param request: HTTP request object
    :param current_user: Current user object
    :return: Current user's information
    """
    return current_user

@router.post("/avatar", response_model=dict)
def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the user's avatar.

    :param file: Uploaded file
    :param current_user: Current user object
    :param db: SQLAlchemy database session
    :return: URL of the uploaded avatar
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG allowed.")

    avatar_url = upload_avatar(file)
    current_user.avatar = avatar_url
    db.commit()
    db.refresh(current_user)

    return {"avatar_url": avatar_url}



router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/request-password-reset")
async def request_password_reset(data: RequestPasswordReset, db: Session = Depends(get_db)):
    """
    Request a password reset link for the user.

    :param data: Request data containing the user's email
    :param db: SQLAlchemy database session
    :return: Success message
    """
    user = users.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = reset_password.generate_reset_token(data.email)
    await reset_password.send_password_reset_email(data.email, token)
    return {"message": "Password reset email sent"}

@router.post("/reset-password")
async def confirm_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Confirm the password reset using the token and new password.

    :param data: Request data containing the token and new password
    :param db: SQLAlchemy database session
    :return: Success message
    """
    updated_user = await reset_password.reset_password(db, data.token, data.new_password)
    if not updated_user:
        raise HTTPException(status_code=400, detail="Invalid token or user")
    return {"message": "Password updated successfully"}