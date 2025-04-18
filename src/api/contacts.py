from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.repository.database.db import get_db
from src.repository import contacts
from src.schemas import ContactCreate, ContactUpdate
from src.services.auth import get_current_user
from src.repository.database.models import User

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.post("/", response_model=ContactCreate)
def create(contact: ContactCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new contact.

    :param contact: Contact data
    :param db: SQLAlchemy database session
    :param current_user: Current user
    :return: Created contact
    """
    try:
        return contacts.create_contact(db, contact, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def read(name: str = None, email: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get all contacts for the current user, optionally filtered by name or email.

    :param name: Optional name to filter contacts by
    :param email: Optional email to filter contacts by
    :param db: SQLAlchemy database session
    :param current_user: Current user
    :return: List of contacts
    """
    return contacts.get_contacts(db, current_user.id, name, email)

@router.get("/{contact_id}")
def read_one(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a specific contact by ID for the current user.

    :param contact_id: ID of the contact
    :param db: SQLAlchemy database session
    :param current_user: Current user
    :return: Contact object if found, None otherwise
    """
    contact = contacts.get_contact(db, contact_id, current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}")
def update(contact_id: int, contact_update: ContactUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update a contact's information.

    :param contact_id: ID of the contact to update
    :param contact_update: Updated contact data
    :param db: SQLAlchemy database session
    :param current_user: Current user
    :return: Updated contact
    """
    updated_contact = contacts.update_contact(db, contact_id, contact_update, current_user.id)
    if not updated_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact

@router.delete("/{contact_id}")
def delete(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a contact by ID for the current user.

    :param contact_id: ID of the contact to delete
    :param db: SQLAlchemy database session
    :param current_user: Current user
    :return: Confirmation message
    """
    deleted_contact = contacts.delete_contact(db, contact_id, current_user.id)
    if not deleted_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"detail": "Contact deleted"}
