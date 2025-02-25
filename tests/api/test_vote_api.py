from fastapi.testclient import TestClient

from msc.database import get_db
from msc.models import Server, User

from .utils import get_auth_header, get_response_body


def test_add_vote(
    session,
    test_client: TestClient,
    user_jack: User,
    server_colcraft: Server,
    mocker,
):
    mocker.patch("msc.utils.api_utils.get_client_ip", return_value="testclient")

    response = test_client.post(
        "/votes",
        headers=get_auth_header(user_jack.id),
        json={
            "server_id": str(server_colcraft.id),
            "minecraft_username": "test",
        },
    )

    assert response.status_code == 200
    assert response.json() == "success"


def test_add_2_votes_24_hours_same_ip(
    session,
    test_client: TestClient,
    user_jack: User,
    server_colcraft: Server,
    mocker,
):
    mocker.patch("msc.utils.api_utils.get_client_ip", return_value="testclient")

    response = test_client.post(
        "/votes",
        headers=get_auth_header(user_jack.id),
        json={
            "server_id": str(server_colcraft.id),
            "minecraft_username": "test",
        },
    )
    assert response.status_code == 200

    response_2 = test_client.post(
        "/votes",
        headers=get_auth_header(user_jack.id),
        json={
            "server_id": str(server_colcraft.id),
            "minecraft_username": "alan",
        },
    )

    assert response_2.status_code == 429

    body = get_response_body(response_2)

    assert body["type"] == "too_many_requests"
    assert (
        body["message"] == "You have already voted for this server in the last 24 hours"
    )
    assert body["data"] == {}


def test_check_vote_info(
    session,
    test_client: TestClient,
    user_jack: User,
    server_colcraft: Server,
    mocker,
):
    mocker.patch("msc.utils.api_utils.get_client_ip", return_value="testclient")

    # first vote
    response = test_client.post(
        "/votes",
        headers=get_auth_header(user_jack.id),
        json={
            "server_id": str(server_colcraft.id),
            "minecraft_username": "test",
        },
    )
    assert response.status_code == 200

    # check vote info
    response = test_client.get(
        "/votes/check",
        headers=get_auth_header(user_jack.id),
        params={
            "server_id": str(server_colcraft.id),
        },
    )
    assert response.status_code == 200

    body = get_response_body(response)

    assert body["has_voted"] is True
    assert body["last_vote"] is not None
    assert isinstance(body["last_vote"], str)
    assert body["time_left_ms"] is not None
    assert isinstance(body["time_left_ms"], int)
    assert body["client_ip"] is not None
    assert isinstance(body["client_ip"], str)
    assert body["client_ip"] == "testclient"
