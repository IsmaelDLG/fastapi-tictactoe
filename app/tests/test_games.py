import pytest
from fastapi import status
from fastapi.testclient import TestClient
from time import time
from .. import main, db
from .utils import override_get_db

main.app.dependency_overrides[db.get_db] = override_get_db

client = TestClient(main.app)

base_url = "/games"

users = []
games = []
auth = {}

@pytest.fixture(autouse=True)
def set_up_tear_down_test(base_headers):
    # Setup: fill with any logic you want
    i = 1
    while len(users) < 2:
        response = client.post(
            "/users",
            headers=base_headers,
            json={
                "username": f"user{i}",
                "password": f"user{i}",
            },
        )
        json = response.json()
        print(f"setup status: {response.status_code} response: {json}")
        users.append(json["id"])
        i += 1
    while len(auth) < 1:
        response = client.post(
            "/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "username": "user1",
                "password": "user1",
            },
        )
        json = response.json()
        print(f"setup status: {response.status_code} response: {json}")
        auth.update({"Authorization": f"{json['type']} {json['token']}"})
    base_headers.update(auth)
    while len(games) < 2:
        response = client.post(
            "/games",
            headers=base_headers,
            json={
                "player1_id": users[0],
                "player2_id": users[1],
            },
        )
        json = response.json()
        print(f"setup status: {response.status_code} response: {json}")
        games.append(json["id"])
    yield
    # Teardown : fill with any logic you want
    


def test_create_player1_invalid(base_headers):
    base_headers.update(auth)
    # 2 users in setup
    (player1, player2) = users
    player3 = max(users) + 1
    print(player1, type(player1), player2, type(player2), player3, type(player3))
    # test game create error when any users does not exist
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={"player1_id": player1, "player2_id": player3},
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "player2 doesn't exist"
    
def test_create_player2_invalid(base_headers):
    base_headers.update(auth)
    # 2 users in setup
    (player1, player2) = users
    player3 = max(users) + 1
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={"player1_id": player3, "player2_id": player1},
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "player1 doesn't exist"
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={"player1_id": player3, "player2_id": player3},
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "player1/2 don't exist"
    
def test_create_players_valid(base_headers):
    base_headers.update(auth)
    # 2 users in setup
    (player1, player2) = users
    player3 = max(users) + 1
    # test game create when users exist
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={
            "player1_id": player1,
            "player2_id": player2,
        },
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_201_CREATED, "is created"


def test_get_all():
    response = client.get(f"{base_url}")
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_200_OK, "is ok"
    assert type(json) == list, "is list"
    
def test_get_one():
    response = client.get(f"{base_url}/{max(games)}")
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_200_OK, "is ok"
    
    response = client.get(f"{base_url}/{min(games) - 1}")
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_404_NOT_FOUND, "is ok"
    
def test_update(base_headers):
    base_headers.update(auth)
    # giro de orden
    response = client.put(f"{base_url}/{max(games)}", headers=base_headers, json={
        "player1_id": users[1],
        "player2_id": users[0],
    })
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_200_OK, "is ok"

def test_delete(base_headers):
    base_headers.update(auth)
    # giro de orden
    response = client.delete(f"{base_url}/{max(games)}", headers=base_headers)
    print(f"status: {response.status_code}")
    assert response.status_code == status.HTTP_204_NO_CONTENT, "is deleted"
    