from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hashes a password using bcrypt.

    :param password: The password to hash
    :return: The hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Verifies a password against a hashed password.

    :param plain: The plain password to verify
    :param hashed: The hashed password to verify against
    :return: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain, hashed)