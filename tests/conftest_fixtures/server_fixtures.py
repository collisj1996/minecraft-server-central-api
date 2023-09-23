import pytest

from msc.models import User
from msc.services import server_service


@pytest.fixture
def server_colcraft(user_jack: User):
    """Returns a server with default values"""

    with open("tests/resources/test_image_base64_string.txt", "r") as f:
        image_base64_string = f.read()

    server = server_service.create_server(
        name="My Server",
        user_id=user_jack.id,
        description="My Server Description",
        java_ip_address="192.168.1.100",
        java_port=8080,
        country_code="GB",
        minecraft_version="1.16.5",
        votifier_ip_address=None,
        votifier_port=None,
        votifier_key=None,
        website="https://www.myserver.com",
        discord="https://discord.gg/myserver",
        banner_base64=image_base64_string,
        gameplay=["Survival", "Creative", "Skyblock"],
    )

    return server


@pytest.fixture
def server_hypixel(user_alan: User):
    """Returns a server with default values"""

    with open("tests/resources/test_image_base64_string.txt", "r") as f:
        image_base64_string = f.read()

    server = server_service.create_server(
        name="Hypixel",
        user_id=user_alan.id,
        description="Hypixel Description",
        java_ip_address="192.168.1.100",
        java_port=8080,
        country_code="GB",
        minecraft_version="1.16.5",
        votifier_ip_address=None,
        votifier_port=None,
        votifier_key=None,
        website="https://www.myserver.com",
        discord="https://discord.gg/myserver",
        banner_base64=image_base64_string,
        gameplay=["Survival", "Creative", "Skyblock"],
    )

    return server
