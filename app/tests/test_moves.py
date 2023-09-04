import pytest
from fastapi import status
from fastapi.testclient import TestClient
from time import time
from datetime import datetime
from .. import main, db
from .utils import override_get_db
from ..routers.moves import find_winner

main.app.dependency_overrides[db.get_db] = override_get_db

client = TestClient(main.app)

base_url = "/games"

users = []
games = []
auth = {}
alt_auth = {}


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
            json={
                "username": users[0]["username"],
                "password": users[0]["username"],
            },
        )
        json = response.json()
        print(f"setup status: {response.status_code} response: {json}")
        auth.update({"Authorization": f"{json['type']} {json['token']}"})
    while len(alt_auth) < 1:
        response = client.post(
            "/login",
            json={
                "username": users[1]["username"],
                "password": users[1]["username"],
            },
        )
        json = response.json()
        print(f"setup status: {response.status_code} response: {json}")
        alt_auth.update({"Authorization": f"{json['type']} {json['token']}"})


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
    games = []


def test_create_move_no_auth():
    response = client.post(f"{base_url}/{games[0]['id']}/moves", json={"position": 1})
    json = response.json()
    print(f"status_code: {response.status_code} json: {json}")
    assert response.status_code == status.HTTP_403_FORBIDDEN, "invalid credentials"


def test_create_move_unexistent_game(base_headers):
    response = client.post(
        f"/{base_url}/1000/moves", headers=base_headers, json={"position": 1}
    )
    json = response.json()
    print(f"status_code: {response.status_code} json: {json}")
    assert response.status_code == status.HTTP_404_NOT_FOUND, "not found"


def test_create_move_invalid_game(base_headers):
    """game 1 is closed, no moves accepted."""
    response = client.post(
        f"{base_url}/{games[0]['id']}/moves",
        headers=base_headers,
        json={"position": 1},
    )
    json = response.json()
    print(f"status_code: {response.status_code} json: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "is closed"
    assert json["detail"].endswith("is closed")


def test_create_move_invalid_turn(base_headers):
    base_headers.update(alt_auth)
    # player2 can not move first
    response = client.post(
        f"{base_url}/{games[1]['id']}/moves",
        headers=base_headers,
        json={"position": 1},
    )
    json = response.json()
    print(f"status_code: {response.status_code} json: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "invalid move"
    assert json["detail"].endswith("invalid move")


def test_create_move_double_move(base_headers):
    # player1 can not move twice
    response = client.post(
        f"{base_url}/{games[1]['id']}/moves",
        headers=base_headers,
        json={"position": 1},
    )
    json = response.json()
    print(f"status_code: {response.status_code} json: {json}")
    response = client.post(
        f"{base_url}/{games[1]['id']}/moves",
        headers=base_headers,
        json={"position": 1},
    )
    json = response.json()
    print(f"status_code: {response.status_code} json: {json}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, "invalid move"
    assert json["detail"].endswith("invalid move")


def test_find_winner():
    (closed_at, winner_id) = find_winner([None for i in range(9)])
    assert closed_at is None, "game not finished"
    assert winner_id is None, "no winner yet"
    (closed_at, winner_id) = find_winner([0, 1, 0, 1, 0, 1, 1, 0, 1])
    assert closed_at is not None, "game finished"
    assert winner_id is None, "draw"
    (closed_at, winner_id) = find_winner([1, 1, None, 0, 0, None, None, None, None])
    assert closed_at is None, "game not finished"
    assert winner_id is None, "no winner yet"
    (closed_at, winner_id) = find_winner([1, 1, 1, 0, 0, None, None, None, None])
    assert closed_at is not None, "game finished"
    assert winner_id == 1, "1 win"
    (closed_at, winner_id) = find_winner([1, 0, 0, 1, 0, 1, 1, None, None])
    assert closed_at is not None, "game finished"
    assert winner_id == 1, "1 win"
    (closed_at, winner_id) = find_winner([0, 1, 1, 0, 0, 1, 1, 1, 0])
    assert closed_at is not None, "game finished"
    assert winner_id == 0, "0 win"
