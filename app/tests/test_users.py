import pytest
from fastapi import status, Depends
from fastapi.testclient import TestClient
from .. import main, db, models
from .utils import override_get_db

main.app.dependency_overrides[db.get_db] = override_get_db

client = TestClient(main.app)

base_url = "/users"


@pytest.fixture(autouse=True)
def set_up_tear_down_test(base_headers):
    # Setup: fill with any logic you want
    response = client.post(base_url, headers=base_headers, json={
        "username": "user1",
        "password": "user1"
    })
    print(f"setup status_code: {response.status_code} json: {response.json()}")
    yield
    # Teardown : fill with any logic you want


def test_create(base_headers):
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={"username": "test01", "password": "test01"},
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_201_CREATED, "is created"

    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={"username": "test01", "password": "test01"},
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "user already exists"


def test_get_all(base_headers):
    response = client.get(f"{base_url}", headers=base_headers)
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_200_OK, "is ok"
    assert type(json) == list, "is list"


def test_get_one(base_headers):
    response = client.get(f"{base_url}/1", headers=base_headers)
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_200_OK, "is ok"
    assert json["username"] == "user1", "is user1"