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


def set_up_users(headers):
    i = 1
    while len(users) < 2:
        response = client.post(
            "/users",
            headers=headers,
            json={
                "username": f"user{i}",
                "password": f"user{i}",
            },
        )
        json = response.json()
        print(f"setup status: {response.status_code} response: {json}")
        users.append(json)
        i += 1
    
    
def set_up_auth():
    while len(auth) < 1:
        response = client.post(
            "/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "username": users[0]["username"],
                "password": users[0]["username"],
            },
        )
        json = response.json()
        print(f"setup status: {response.status_code} response: {json}")
        auth.update({"Authorization": f"{json['type']} {json['token']}"})
    

def set_up_games(headers):
    # Setup: fill with any logic you want
    while len(games) < 2:
        response = client.post(
            "/games",
            headers=headers,
            json={
                "player1_id": users[0]["id"],
                "player2_id": users[1]["id"],
            },
        )
        json = response.json()
        print(f"setup status: {response.status_code} response: {json}")
        games.append(json)
        
@pytest.fixture(autouse=True)
def set_up_and_tear_down(base_headers):
    set_up_users(base_headers)
    set_up_auth()
    base_headers.update(auth)
    set_up_games(base_headers)
    yield
    # Teardown here
    


def test_create_player1_invalid(base_headers):
    base_headers.update(auth)
    # 2 users in setup
    (player1, player2) = users
    # test game create error when any users does not exist
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={"player1_id": player1["id"], "player2_id": player2["id"] + 1},
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "player2 doesn't exist"
    
def test_create_player2_invalid(base_headers):
    base_headers.update(auth)
    # 2 users in setup
    (player1, player2) = users
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={"player1_id": player1["id"], "player2_id": player2["id"] + 1},
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "player1 doesn't exist"
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={"player1_id": player2["id"] + 1, "player2_id": player2["id"] + 1},
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "player1/2 don't exist"
    
def test_create_players_valid(base_headers):
    base_headers.update(auth)
    # 2 users in setup
    (player1, player2) = users
    # test game create when users exist
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={
            "player1_id": player1["id"],
            "player2_id": player2["id"],
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
    response = client.get(f"{base_url}/{games[-1]['id']}")
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_200_OK, "is ok"
    
    response = client.get(f"{base_url}/{games[0]['id'] - 1}")
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_404_NOT_FOUND, "is ok"
    
def test_update(base_headers):
    base_headers.update(auth)
    # giro de orden
    response = client.put(f"{base_url}/{games[-1]['id']}", headers=base_headers, json={
        "player1_id": users[1]["id"],
        "player2_id": users[0]["id"],
    })
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_200_OK, "is ok"

def test_delete(base_headers):
    base_headers.update(auth)
    # giro de orden
    response = client.delete(f"{base_url}/{games[-1]['id']}", headers=base_headers)
    print(f"status: {response.status_code}")
    assert response.status_code == status.HTTP_204_NO_CONTENT, "is deleted"
    