def test_upload_avatar(client):
    with open("tests/avatar_sample.jpg", "rb") as avatar:
        response = client.post("/avatar", files={"file": avatar})
        assert response.status_code == 200
        assert "http" in response.json()["avatar_url"]