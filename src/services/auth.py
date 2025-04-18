from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import os
from src.repository import users
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from src.repository.database.db import get_db
from src.repository.database.models import User
import cloudinary
import cloudinary.uploader
from src.services.cache import get_cached_user, set_cached_user

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def upload_avatar(file: UploadFile):
    """
    Uploads an avatar image to Cloudinary and returns the secure URL.

    :param file: The image file to upload
    :return: The secure URL of the uploaded image
    """
    result = cloudinary.uploader.upload(file.file)
    return result.get("secure_url")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Retrieves the current user from JWT token, using Redis cache if available.

    :param token: The JWT token
    :param db: SQLAlchemy session
    :return: The user object
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    payload = decode_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception

    email = payload["sub"]

    cached_user = get_cached_user(email)
    if cached_user:
        return User(**cached_user)

    user = users.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    set_cached_user(email, user.dict())
    return user

def create_access_token(data: dict):
    """
    Creates a JWT access token.

    :param data: The data to encode in the token
    :return: The encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    """
    Decodes a JWT token and returns the payload.

    :param token: The JWT token to decode
    :return: The decoded payload if valid, None otherwise
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None