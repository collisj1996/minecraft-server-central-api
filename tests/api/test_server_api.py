from fastapi.testclient import TestClient

from msc.config import config
from msc.models import Server, User

from .utils import get_auth_header, get_response_body


def test_get_my_servers(
    session,
    test_client: TestClient,
    user_jack: User,
    server_colcraft: Server,
):
    config.development_mode = True
    response = test_client.get(
        "/servers/mine",
        headers=get_auth_header(user_jack.id),
    )
    assert response.status_code == 200


def test_get_my_servers_no_auth(
    session,
    test_client: TestClient,
    user_jack: User,
    server_colcraft: Server,
):
    config.development_mode = True
    response = test_client.get(
        "/servers/mine",
    )
    assert response.status_code == 401
