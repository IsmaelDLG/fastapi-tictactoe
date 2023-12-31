import pytest
from fastapi import status
from fastapi.testclient import TestClient
from time import time
from datetime import datetime
from .. import main, db
from .utils import override_get_db

main.app.dependency_overrides[db.get_db] = override_get_db

client = TestClient(main.app)

base_url = "/games"

users = []
games = []
auth = {}


def set_up_users(headers):
    while len(users) < 2:
        response = client.post(
            "/users",
            headers=headers,
            json={
                "username": f"user{time()}",
                "password": f"user{time()}",
            },
        )
        json = response.json()
        print(f"setup status: {response.status_code} response: {json}")
        users.append(json)


def set_up_auth(headers):
    while len(auth) < 1:
        response = client.post(
            "/login",
            headers=headers,
            json={
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
            f"{base_url}",
            headers=headers,
            json={
                "player1_id": users[0]["id"],
                "player2_id": users[1]["id"],
            },
        )
        json = response.json()
        print(f"setup status: {response.status_code} response: {json}")
        games.append(json["game"])
    # close game 1
    if games[0]["closed_at"] is None:
        response = client.patch(
            f"{base_url}/{games[0]['id']}",
            headers=headers,
            json={"closed_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")},
        )
        json = response.json()
        print(f"setup status: {response.status_code} response: {json}")
        games[0] = json["game"]


@pytest.fixture(autouse=True)
def set_up_and_tear_down(base_headers):
    set_up_users(base_headers)
    set_up_auth(base_headers)
    base_headers.update(auth)
    set_up_games(base_headers)
    yield
    # Teardown here


def test_create_player2_invalid(base_headers):
    # 2 users in setup
    (player1, player2) = users
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={"player2_id": 500},
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "player1 doesn't exist"


def test_create_player_equal(base_headers):
    (player1, player2) = users
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={"player2_id": player1["id"]},
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "players equal"


def test_create_players_valid(base_headers):
    # 2 users in setup
    (player1, player2) = users
    # test game create when users exist
    response = client.post(
        f"{base_url}",
        headers=base_headers,
        json={
            "player2_id": player2["id"],
        },
    )
    json = response.json()
    print(f"status: {response.status_code} response: {json}")
    assert response.status_code == status.HTTP_201_CREATED, "is created"
    assert json.get("game") is not None, "game data"
    assert json.get("moves") is not None, "move data"


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


# def test_update(base_headers):
#     # giro de orden
#     response = client.put(f"{base_url}/{games[-1]['id']}", headers=base_headers, json={
#         "player1_id": users[1]["id"],
#         "player2_id": users[0]["id"],
#     })
#     json = response.json()
#     print(f"status: {response.status_code} response: {json}")
#     assert response.status_code == status.HTTP_200_OK, "is ok"


def test_delete(base_headers):
    # giro de orden
    response = client.delete(f"{base_url}/{games[-1]['id']}", headers=base_headers)
    print(f"status: {response.status_code}")
    assert response.status_code == status.HTTP_204_NO_CONTENT, "is deleted"


def test_patch_no_auth(base_headers):
    response = client.patch(f"{base_url}/{games[0]['id']}", json={})
    print(f"status: {response.status_code}")
    assert response.status_code == status.HTTP_403_FORBIDDEN, "invalid credentials"


def test_patch_invalid_combination(base_headers):
    response = client.patch(
        f"{base_url}/{games[0]['id']}", headers=base_headers, json={"winner_id": True}
    )
    json = response.json()
    print(f"status: {response.status_code} json: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "invalid combination"


def test_patch(base_headers):
    response = client.patch(
        f"{base_url}/{games[0]['id']}",
        headers=base_headers,
        json={
            "closed_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "winner_id": True,
        },
    )
    json = response.json()
    print(f"status: {response.status_code} json: {json}")
    assert response.status_code == status.HTTP_200_OK, "is ok"
