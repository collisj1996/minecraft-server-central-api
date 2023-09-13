import pytest

from msc.models import User
from msc.services import server_service


@pytest.fixture
def server_default(user_default: User):
    """Returns a server with default values"""

    with open("tests/resources/test_image_base64_string.txt", "r") as f:
        image_base64_string = f.read()

    server = server_service.create_server(
        name="My Server",
        user_id=user_default.id,
        description="My Server Description",
        ip_address="192.168.1.100",
        port=8080,
        country_code="GB",
        minecraft_version="1.16.5",
        votifier_ip_address=None,
        votifier_port=None,
        votifier_key=None,
        website="https://www.myserver.com",
        discord="https://discord.gg/myserver",
        banner_base64=image_base64_string,
    )

    return server
