from msc.services import server_service, vote_service
from io import BytesIO
import base64
import pytest

from msc.models import Server, User


def test_get_servers_no_servers(session):
    """Tests getting servers - no servers"""

    servers = server_service.get_servers()

    assert servers == []


def test_get_servers(session, server_colcraft: Server, server_hypixel: Server,):
    """Tests getting servers"""

    servers = server_service.get_servers()

    assert len(servers) == 2

    hypixel_server = next(s for s in servers if s[0].id == server_hypixel.id)
    colcraft_server = next(s for s in servers if s[0].id == server_colcraft.id)

    assert hypixel_server
    assert hypixel_server[1] == 0
    assert hypixel_server[2] == 0
    assert colcraft_server
    assert colcraft_server[1] == 0
    assert colcraft_server[2] == 0


def test_get_servers_with_votes(session, server_colcraft: Server, server_hypixel: Server,):
    """Tests getting servers with votes"""

    # 2 votes for colcraft
    vote_service.add_vote(server_id=server_colcraft.id, client_ip="192.168.0.1")
    vote_service.add_vote(server_id=server_colcraft.id, client_ip="11.11.11.11")

    # 1 vote for hypixel
    vote_service.add_vote(server_id=server_hypixel.id, client_ip="192.168.0.1")

    servers = server_service.get_servers()

    assert len(servers) == 2

    hypixel_server = next(s for s in servers if s[0].id == server_hypixel.id)
    colcraft_server = next(s for s in servers if s[0].id == server_colcraft.id)

    assert hypixel_server
    assert hypixel_server[1] == 1
    assert hypixel_server[2] == 1
    assert colcraft_server
    assert colcraft_server[1] == 2
    assert colcraft_server[2] == 2


def test_get_servers_with_votes_order(
    session, server_colcraft: Server, server_hypixel: Server,
):
    """Tests getting servers with votes - order"""

    # 2 votes for colcraft
    vote_service.add_vote(server_id=server_colcraft.id, client_ip="192.168.0.1")
    vote_service.add_vote(server_id=server_colcraft.id, client_ip="11.11.11.11")

    servers = server_service.get_servers()

    assert len(servers) == 2

    # colcraft should be first as it has the most votes
    assert servers[0][0].id == server_colcraft.id

    # now gives 3 votes to hypixel
    vote_service.add_vote(server_id=server_hypixel.id, client_ip="192.168.0.1")
    vote_service.add_vote(server_id=server_hypixel.id, client_ip="192.168.0.2")
    vote_service.add_vote(server_id=server_hypixel.id, client_ip="192.168.0.3")

    servers = server_service.get_servers()

    assert len(servers) == 2

    # hypixel should be first as it has the most votes
    assert servers[0][0].id == server_hypixel.id


def test_get_servers_with_votes_monthly(session, server_colcraft: Server, votes_colcraft_20_last_month, votes_colcraft_20_this_month,):
    """Tests getting servers with votes that are monthly"""

    servers = server_service.get_servers()

    assert len(servers) == 1

    colcraft_server = next(s for s in servers if s[0].id == server_colcraft.id)

    assert colcraft_server
    # total votes
    assert colcraft_server[1] == 40
    # votes this month
    assert colcraft_server[2] == 20


def test_validate_banner_valid_gif(session):
    """Tests validating a banner that is a valid gif and the correct size"""

    with open("tests/resources/test_image_base64_string.txt", "r") as f:
        image_base64_string = f.read()

    # Remove metadata from base64 string
    base64_data = image_base64_string.split("base64,")[1]

    # Decode the base64 image
    decoded_data = base64.b64decode(base64_data.encode() + b"==")

    # Create a BytesIO object from the decoded image
    image_data = BytesIO(decoded_data)

    img = server_service._validate_banner(image_data=image_data)

    assert img
    assert img.size == (468, 60)
    assert img.format == "GIF"


def test_create_server(session, user_jack: User,):
    """Test that a server can be created"""

    assert session.query(Server).count() == 0

    server = server_service.create_server(
        name="My Server",
        user_id=user_jack.id,
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
    )

    assert server
    assert server.id
    assert server.name == "My Server"

    assert session.query(Server).count() == 1


def test_one_server_per_user(session, user_jack: User, server_colcraft: Server,):
    """Test that only one server can be created per user"""

    with pytest.raises(Exception) as e:
        server = server_service.create_server(
            name="My Server",
            user_id=user_jack.id,
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
        )

    assert str(e.value) == "User already has a server"