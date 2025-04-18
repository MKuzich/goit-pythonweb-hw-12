def test_create_contact(client):
    response = client.post("/contacts/", json={
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "123456789"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_get_contacts(client):
    response = client.get("/contacts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)