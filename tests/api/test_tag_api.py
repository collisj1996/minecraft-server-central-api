from fastapi.testclient import TestClient

from msc.config import config
from msc.constants import ALLOWED_TAGS
from msc.models import User

from .utils import get_auth_header, get_response_body


def test_get_my_servers(
    session,
    test_client: TestClient,
    user_jack: User,
):
    config.development_mode = True

    response = test_client.get(
        "/tags",
        headers=get_auth_header(user_jack.id),
    )
    assert response.status_code == 200
    body = get_response_body(response)

    assert body == ALLOWED_TAGS

    config.development_mode = False
