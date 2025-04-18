from sqlalchemy.orm import Session
from src.repository.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate

def create_contact(db: Session, contact: ContactCreate, user_id: int):
    """
    Create a new contact in the database.
    
    :param db: SQLAlchemy database session
    :param contact: Contact data
    :return: Created contact
    """
    existing_contact = db.query(Contact).filter(Contact.email == contact.email,
        Contact.user_id == user_id).first()
    if existing_contact:
        raise ValueError("A contact with this email already exists")

    db_contact = Contact(**contact.dict(), user_id=user_id)
    db.add(db_contact)

    try:
        db.commit()
        db.refresh(db_contact)
        return db_contact
    except Exception as e:
        db.rollback()
        raise ValueError("Error: This email is already taken")

def get_contacts(db: Session, user_id: int, name: str = None, email: str = None):
    """
    Get all contacts for a user, optionally filtered by name or email.

    :param db: SQLAlchemy database session
    :param user_id: ID of the user
    :param name: Optional name to filter contacts by
    :param email: Optional email to filter contacts by
    :return: List of contacts
    """
    query = db.query(Contact).filter(Contact.user_id == user_id)
    if name:
        query = query.filter((Contact.first_name.ilike(f"%{name}%")) | (Contact.last_name.ilike(f"%{name}%")))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.all()

def get_contact(db: Session, contact_id: int, user_id: int):
    """
    Get a specific contact by ID for a user.

    :param db: SQLAlchemy database session
    :param contact_id: ID of the contact
    :param user_id: ID of the user
    :return: Contact object if found, None otherwise
    """
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()

def update_contact(db: Session, contact_id: int, contact_update: ContactUpdate, user_id: int):
    """
    Update a contact's information.

    :param db: SQLAlchemy database session
    :param contact_id: ID of the contact to update
    :param contact_update: ContactUpdate schema with updated data
    :param user_id: ID of the user
    :return: Updated contact object if successful, None otherwise
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()
    if not contact:
        return None
    for key, value in contact_update.dict(exclude_unset=True).items():
        setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    return contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Delete a contact by ID for a user.

    :param db: SQLAlchemy database session
    :param contact_id: ID of the contact to delete
    :param user_id: ID of the user
    :return: Deleted contact object if successful, None otherwise
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact
