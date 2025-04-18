from src.services import auth
from src.services.security import get_password_hash, verify_password

def test_password_hashing():
    password = "strongpass"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)

def test_create_access_token():
    token = auth.create_access_token({"sub": "testuser"})
    assert isinstance(token, str)

def test_decode_token():
    token = auth.create_access_token({"sub": "testuser"})
    data = auth.decode_token(token)
    assert data["sub"] == "testuser"