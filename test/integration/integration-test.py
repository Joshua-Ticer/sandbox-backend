import httpx

BASE_URL = "http://localhost:3000"


def test_health():
    response = httpx.get(f"{BASE_URL}/health/")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert "time" in body


def test_create_and_get_user():
    create_response = httpx.post(
        f"{BASE_URL}/users/",
        json={
            "name": "IntegrationUser",
            "age": 25,
            "elo": 1200,
        },
    )

    assert create_response.status_code == 200

    created = create_response.json()

    user_id = created["id"]

    get_response = httpx.get(
        f"{BASE_URL}/users/{user_id}"
    )

    assert get_response.status_code == 200

    fetched = get_response.json()

    assert fetched["id"] == user_id
    assert fetched["name"] == "IntegrationUser"
    assert fetched["age"] == 25
    assert fetched["elo"] == 1200


def test_get_missing_user():
    response = httpx.get(
        f"{BASE_URL}/users/999999"
    )

    assert response.status_code == 404


def test_list_users():
    httpx.post(
        f"{BASE_URL}/users/",
        json={
            "name": "ListUser",
            "age": 30,
            "elo": 1300,
        },
    )

    response = httpx.get(
        f"{BASE_URL}/users/"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_match_updates_elo():
    user1 = httpx.post(
        f"{BASE_URL}/users/",
        json={
            "name": "Player1",
            "age": 20,
            "elo": 1200,
        },
    ).json()

    user2 = httpx.post(
        f"{BASE_URL}/users/",
        json={
            "name": "Player2",
            "age": 21,
            "elo": 1200,
        },
    ).json()

    before1 = httpx.get(
        f"{BASE_URL}/users/{user1['id']}"
    ).json()

    before2 = httpx.get(
        f"{BASE_URL}/users/{user2['id']}"
    ).json()

    match_response = httpx.post(
        f"{BASE_URL}/match/{user1['id']}/{user2['id']}"
    )

    assert match_response.status_code == 200

    after1 = httpx.get(
        f"{BASE_URL}/users/{user1['id']}"
    ).json()

    after2 = httpx.get(
        f"{BASE_URL}/users/{user2['id']}"
    ).json()

    assert (
        after1["elo"] != before1["elo"]
        or after2["elo"] != before2["elo"]
    )


def test_match_invalid_users():
    response = httpx.post(
        f"{BASE_URL}/match/99999/88888"
    )

    assert response.status_code == 400