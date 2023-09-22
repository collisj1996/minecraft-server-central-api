import base64
from io import BytesIO
from uuid import uuid4

import pytest

from msc.models import Server, User, Vote
from msc.services import server_service, vote_service, user_service


def test_get_servers_no_servers(session):
    """Tests getting servers - no servers"""

    servers, total_servers = server_service.get_servers()

    assert servers == []
    assert total_servers == 0


def test_get_servers(
    session,
    server_colcraft: Server,
    server_hypixel: Server,
):
    """Tests getting servers"""

    servers, total_servers = server_service.get_servers()

    assert len(servers) == 2
    assert total_servers == 2

    hypixel_server = next(s for s in servers if s[0].id == server_hypixel.id)
    colcraft_server = next(s for s in servers if s[0].id == server_colcraft.id)

    assert hypixel_server
    assert hypixel_server[1] == 0
    assert hypixel_server[2] == 0
    assert colcraft_server
    assert colcraft_server[1] == 0
    assert colcraft_server[2] == 0


def test_get_servers_with_votes(
    session,
    server_colcraft: Server,
    server_hypixel: Server,
):
    """Tests getting servers with votes"""

    # 2 votes for colcraft
    vote_service.add_vote(server_id=server_colcraft.id, client_ip="192.168.0.1")
    vote_service.add_vote(server_id=server_colcraft.id, client_ip="11.11.11.11")

    # 1 vote for hypixel
    vote_service.add_vote(server_id=server_hypixel.id, client_ip="192.168.0.1")

    servers, total_servers = server_service.get_servers()

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
    session,
    server_colcraft: Server,
    server_hypixel: Server,
):
    """Tests getting servers with votes - order"""

    # 2 votes for colcraft
    vote_service.add_vote(server_id=server_colcraft.id, client_ip="192.168.0.1")
    vote_service.add_vote(server_id=server_colcraft.id, client_ip="11.11.11.11")

    servers, total_servers = server_service.get_servers()

    assert len(servers) == 2
    assert total_servers == 2

    # colcraft should be first as it has the most votes
    assert servers[0][0].id == server_colcraft.id

    # now gives 3 votes to hypixel
    vote_service.add_vote(server_id=server_hypixel.id, client_ip="192.168.0.1")
    vote_service.add_vote(server_id=server_hypixel.id, client_ip="192.168.0.2")
    vote_service.add_vote(server_id=server_hypixel.id, client_ip="192.168.0.3")

    servers, total_servers = server_service.get_servers()

    assert len(servers) == 2
    assert total_servers == 2

    # hypixel should be first as it has the most votes
    assert servers[0][0].id == server_hypixel.id


def test_get_servers_with_votes_monthly(
    session,
    server_colcraft: Server,
    votes_colcraft_20_last_month,
    votes_colcraft_20_this_month,
):
    """Tests getting servers with votes that are monthly"""

    servers, total_servers = server_service.get_servers()

    assert len(servers) == 1
    assert total_servers == 1

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


def test_create_server(
    session,
    user_jack: User,
):
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
        gameplay=["Survival", "Creative", "Skyblock"],
    )

    assert server
    assert server.id
    assert server.name == "My Server"

    assert session.query(Server).count() == 1


def test_one_server_per_user(
    session,
    user_jack: User,
    server_colcraft: Server,
):
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
            gameplay=["Survival", "Creative", "Skyblock"],
        )

    assert str(e.value) == "User already has a server"


def _create_multiple_servers_for_pagination(session):
    """Creates multiple servers for testing pagination"""

    for i in range(1, 35):
        # create a new user
        user = user_service.add_user(
            user_id=uuid4(),
            username=f"test user {i}",
            email=f"testuser{i}@gmail.com",
        )

        # create a new server for the user
        server = server_service.create_server(
            name=f"My Server {i}",
            user_id=user.id,
            description="My Server Description",
            ip_address=f"1.2.3.{i}",
            port=8080,
            country_code="GB",
            minecraft_version="1.16.5",
            votifier_ip_address=None,
            votifier_port=None,
            votifier_key=None,
            website="https://www.myserver.com",
            discord="https://discord.gg/myserver",
            gameplay=["Survival", "Creative", "Skyblock"],
        )

        # force add i votes for the server
        # directly add vote to database
        for _ in range(i):
            vote = Vote(
                server_id=server.id,
                client_ip_address="1.2.3.4",
            )
            session.add(vote)

    session.commit()


def test_get_servers_pagination(session):
    """Tests getting servers with pagination"""

    _create_multiple_servers_for_pagination(session)

    pages = 4
    per_page = 10

    for page in range(1, pages + 1):
        servers, total_servers = server_service.get_servers(
            page=page, page_size=per_page
        )

        for i, server in enumerate(servers):
            assert (
                server[0].name
                == f"My Server {total_servers - ((page - 1) * per_page + i)}"
            )


def test_update_server_all_properties(
    session,
    user_jack: User,
    server_colcraft: Server,
):
    """Tests updating all properties on a server"""

    updated_server = server_service.update_server(
        server_id=server_colcraft.id,
        user_id=user_jack.id,
        name="UPDATED NAME",
        description="UPDATED DESCRIPTION",
        ip_address="0.0.0.0",
        port=9999,
        country_code="FR",
        minecraft_version="9.9.9",
        votifier_ip_address="0.0.0.0",
        votifier_port=9999,
        votifier_key="UPDATED KEY",
        website="https://www.updated.com",
        discord="https://discord.gg/updated",
        banner_base64=None,
        gameplay=["Survival", "Creative", "Skyblock", "Bedwars", "Minigames"],
    )

    assert updated_server
    assert updated_server.name == "UPDATED NAME"
    assert updated_server.description == "UPDATED DESCRIPTION"
    assert updated_server.ip_address == "0.0.0.0"
    assert updated_server.port == 9999
    assert updated_server.country_code == "FR"
    assert updated_server.minecraft_version == "9.9.9"
    assert updated_server.votifier_ip_address == "0.0.0.0"
    assert updated_server.votifier_port == 9999
    assert updated_server.votifier_key == "UPDATED KEY"
    assert updated_server.website == "https://www.updated.com"
    assert updated_server.discord == "https://discord.gg/updated"
    assert updated_server.banner_url is None
    for updated_gameplay in [g.name for g in updated_server.gameplay]:
        assert updated_gameplay in [
            "Survival",
            "Creative",
            "Skyblock",
            "Bedwars",
            "Minigames",
        ]


def test_update_server_some_properties(
    session,
    user_jack: User,
):
    """Test updating some properties on a server"""

    # first create a server
    server = server_service.create_server(
        name="My Server",
        user_id=user_jack.id,
        description="My Server Description",
        ip_address="0.0.0.0",
        port=1234,
        country_code="GB",
        minecraft_version="1.16.5",
        votifier_ip_address=None,
        votifier_port=None,
        votifier_key=None,
        website="https://www.myserver.com",
        discord="https://discord.gg/myserver",
        gameplay=["Survival", "Creative", "Skyblock"],
    )

    # now update some properties
    updated_server = server_service.update_server(
        server_id=server.id,
        user_id=user_jack.id,
        name="UPDATED NAME",
        description="UPDATED DESCRIPTION",
    )

    assert updated_server
    assert updated_server.name == "UPDATED NAME"
    assert updated_server.description == "UPDATED DESCRIPTION"
    assert updated_server.ip_address == "0.0.0.0"
    assert updated_server.port == 1234
    assert updated_server.country_code == "GB"
    assert updated_server.minecraft_version == "1.16.5"
    assert updated_server.votifier_ip_address is None
    assert updated_server.votifier_port is None
    assert updated_server.votifier_key is None
    assert updated_server.website == "https://www.myserver.com"
    assert updated_server.discord == "https://discord.gg/myserver"
    assert updated_server.banner_url is None


def test_update_server_not_owned(
    session,
    user_jack: User,
    server_hypixel: Server,
):
    """Test for failure on updating a server that is not owned by the user"""

    with pytest.raises(Exception) as e:
        updated_server = server_service.update_server(
            server_id=server_hypixel.id,
            user_id=user_jack.id,
            name="UPDATED NAME",
            description="UPDATED DESCRIPTION",
        )

    assert str(e.value) == "You do not own this server"


def test_delete_server(
    session,
    user_jack: User,
    server_colcraft: Server,
):
    """Tests deleting a server"""

    deleted_server_id = server_service.delete_server(
        server_id=server_colcraft.id,
        user_id=user_jack.id,
    )

    assert deleted_server_id == server_colcraft.id

    assert session.query(Server).count() == 0


def test_delete_server_not_owned(
    session,
    user_jack: User,
    server_hypixel: Server,
):
    """Test for failure on deleting a server that is not owned by the user"""

    with pytest.raises(Exception) as e:
        deleted_server_id = server_service.delete_server(
            server_id=server_hypixel.id,
            user_id=user_jack.id,
        )

    assert str(e.value) == "You do not own this server"


def test_get_server(session, server_colcraft: Server):
    """Tests getting a server"""

    server, total_votes, monthly_votes, rank = server_service.get_server(
        server_id=server_colcraft.id
    )

    assert server
    assert server.id == server_colcraft.id
    assert server.name == server_colcraft.name
    assert total_votes == 0
    assert monthly_votes == 0
    assert rank == 1


def test_get_my_servers(
    session,
    user_jack: User,
    user_alan: User,
    server_colcraft: Server,
    server_hypixel: Server,
):
    """Tests getting my servers"""

    # create another server for jack
    server_2 = server_service.create_server(
        name="My Server 2",
        user_id=user_jack.id,
        description="My Server Description",
        ip_address="1.2.3.4",
        gameplay=["Survival", "Creative", "Skyblock"],
        country_code="GB",
        minecraft_version="1.16.5",
    )

    # get all servers
    servers = server_service.get_servers()[0]

    assert len(servers) == 3

    # get my servers
    my_servers = server_service.get_my_servers(user_jack.id)

    assert len(my_servers) == 2

    for s in my_servers:
        assert s[0].id in [server_colcraft.id, server_2.id]

    # get my servers for alan
    my_servers = server_service.get_my_servers(user_alan.id)

    for s in my_servers:
        assert s[0].id in [server_hypixel.id]
