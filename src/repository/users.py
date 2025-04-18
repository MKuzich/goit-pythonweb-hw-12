from sqlalchemy.orm import Session
from src.repository.database.models import User
from src.schemas import UserCreate
from src.services.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    """
    Get a user by their email address.

    :param db: SQLAlchemy database session
    :param email: Email address of the user
    :return: User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    """
    Create a new user in the database.

    :param db: SQLAlchemy database session
    :param user: User data
    :return: Created user
    """
    hashed_pw = get_password_hash(user.password)
    db_user = User(username = user.username, email=user.email, hashed_password=hashed_pw, confirmed=False)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user