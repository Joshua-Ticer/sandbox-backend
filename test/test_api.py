from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from app import crud
from app import main

client = TestClient(app)


def test_health():
    response = client.get("/health/")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert "time" in body


def test_create_user(monkeypatch):
    created_user = {
        "id": 1,
        "name": "Josh",
        "age": 25,
        "elo": 1200,
    }

    monkeypatch.setattr(crud, "create_item", lambda db, item: created_user)

    monkeypatch.setattr(main, "delete_cache", AsyncMock())

    response = client.post(
        "/users/",
        json={
            "name": "Josh",
            "age": 25,
            "elo": 1200,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Josh"
    assert data["age"] == 25
    assert data["elo"] == 1200


def test_get_user_not_found(monkeypatch):

    monkeypatch.setattr(main, "get_cache", AsyncMock(return_value=None))
    monkeypatch.setattr(crud, "get_item", lambda db, id: None)

    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_user_cache_hit(monkeypatch):

    cached_user = {
        "id": 1,
        "name": "Josh",
        "age": 25,
        "elo": 1200,
    }

    monkeypatch.setattr(main, "get_cache", AsyncMock(return_value=cached_user))

    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_user_cache_miss(monkeypatch):
    user = {
        "id": 1,
        "name": "Josh",
        "age": 25,
        "elo": 1200,
    }

    monkeypatch.setattr(main, "get_cache", AsyncMock(return_value=None))

    monkeypatch.setattr(main, "set_cache", AsyncMock())

    monkeypatch.setattr(crud, "get_item", lambda db, id: user)

    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_match_success(monkeypatch):
    monkeypatch.setattr(
        crud, "simulate_match", lambda db, u1, u2: {"winner": u1, "loser": u2}
    )

    monkeypatch.setattr(main, "delete_cache", AsyncMock())

    response = client.post("/match/1/2")

    assert response.status_code == 200

    data = response.json()

    assert data["winner"] == 1
    assert data["loser"] == 2


def test_match_failure(monkeypatch):
    def fake_match(db, u1, u2):
        raise ValueError("Invalid user")

    monkeypatch.setattr(crud, "simulate_match", fake_match)

    response = client.post("/match/1/2")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid user"
