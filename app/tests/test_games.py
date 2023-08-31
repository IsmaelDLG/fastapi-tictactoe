from fastapi import status
from fastapi.testclient import TestClient
from ..main import app
from ..schemas import GameResponse

client = TestClient(app)

base_url = "/games"


def test_create(base_headers):
    response = client.post(f"{base_url}", headers=base_headers, json={})
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_201_CREATED, "is created"


def test_get_all():
    response = client.get("/games")
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_200_OK, "is ok"
    assert type(json) == list, "is list"
