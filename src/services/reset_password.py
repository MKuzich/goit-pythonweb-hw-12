from datetime import datetime, timedelta
from jose import jwt, JWTError
from src.services.email import send_email  # реалізуй, або заміни mock-ом
from src.repository import users
from src.services.security import get_password_hash
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def generate_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

async def send_password_reset_email(email: str, token: str):
    """
    Send a password reset email to the user with a link to reset their password.
    
    :param email: The email address of the user.
    :param token: The JWT token for password reset.
    :return: None
    """
    reset_link = f"http://localhost:8000/api/auth/reset-password?token={token}"
    subject = "Password Reset Request"
    body = f"Click the link to reset your password: {reset_link}"
    await send_email(email, subject, body)

async def reset_password(db, token: str, new_password: str):
    """
    Reset the user's password using the provided token and new password.

    :param db: The database session.
    :param token: The JWT token for password reset.
    :param new_password: The new password to set.
    :return: The updated user object or None if the token is invalid or user not found.
    """
    email = verify_reset_token(token)
    if not email:
        return None
    user = users.get_user_by_email(db, email)
    if not user:
        return None
    hashed = get_password_hash(new_password)
    user.hashed_password = hashed
    db.commit()
    return user