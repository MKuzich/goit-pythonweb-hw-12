from src.repository import contacts
from src.schemas import ContactCreate
from src.repository.database.models import Contact
from sqlalchemy.orm import Session

class FakeDB:
    def __init__(self):
        self.contacts = []

    def query(self, model):
        return self

    def filter(self, *args):
        return self

    def first(self):
        return None

    def add(self, contact):
        self.contacts.append(contact)

    def commit(self):
        pass

    def refresh(self, contact):
        pass

def test_create_contact_repo():
    fake_db = FakeDB()
    contact = ContactCreate(first_name="A", last_name="B", email="a@b.com", phone="123")
    result = contacts.create_contact(fake_db, contact)
    assert result.email == "a@b.com"