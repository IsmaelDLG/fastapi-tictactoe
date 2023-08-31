from fastapi import status
from fastapi.testclient import TestClient
from ..main import app
from ..schemas import UserResponse

client = TestClient(app)

base_url = "/users"


def test_create(base_headers):
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={"username": "test03", "password": "test03"},
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_201_CREATED, "is created"
