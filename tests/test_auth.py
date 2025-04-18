def test_signup(client):
    response = client.post("/auth/signup", json={
        "email": "newuser@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 201
    assert "email" in response.json()

def test_login_invalid(client):
    response = client.post("/auth/login", data={
        "username": "invalid@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401