from fastapi.testclient import TestClient

from msc.config import config
from msc.models import User

from .utils import get_auth_header, get_response_body
from msc.constants import ALLOWED_TAGS


def test_get_versions(
    session,
    test_client: TestClient,
    user_jack: User,
):
    config.development_mode = True

    # # add some minecraft versions
    # version_1 = MinecraftVersion(
    #     version="1.0.0",
    #     is_latest=False,
    #     type=VersionType.RELEASE,
    #     release_time=datetime.utcnow() - timedelta(minutes=5),
    # )

    # version_2 = MinecraftVersion(
    #     version="2.0.0",
    #     is_latest=False,
    #     type=VersionType.RELEASE,
    #     release_time=datetime.utcnow() - timedelta(minutes=4),
    # )

    # version_2_1 = MinecraftVersion(
    #     version="2.1.0",
    #     is_latest=True,
    #     type=VersionType.RELEASE,
    #     release_time=datetime.utcnow(),
    # )

    # versions = session.query(MinecraftVersion).all()

    # session.add_all([version_1, version_2, version_2_1])
    # session.commit()

    response = test_client.get(
        "/versions",
        headers=get_auth_header(user_jack.id),
    )
    assert response.status_code == 200
    body = get_response_body(response)

    assert len(body) > 0

    config.development_mode = False
