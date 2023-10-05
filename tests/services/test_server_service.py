import base64
from io import BytesIO
from uuid import uuid4

import pytest

from msc.errors import BadRequest, NotFound
from msc.models import Server, User, Vote
from msc.services import server_service, user_service, vote_service
from msc.services.server_service import GetServersInfo, GetServerInfo


def test_get_servers_no_servers(session):
    """Tests getting servers - no servers"""

    servers_info: GetServersInfo = server_service.get_servers(db=session)

    assert servers_info.servers == []
    assert servers_info.total_servers == 0


def test_get_servers(
    session,
    server_colcraft: Server,
    server_hypixel: Server,
):
    """Tests getting servers"""

    servers_info: GetServersInfo = server_service.get_servers(db=session)

    servers = servers_info.servers
    total_servers = servers_info.total_servers

    assert len(servers) == 2
    assert total_servers == 2

    hypixel_server_info = next(s for s in servers if s.server.id == server_hypixel.id)
    hypixel = hypixel_server_info.server
    hypixel_total_votes = hypixel_server_info.total_votes
    hypixel_votes_this_month = hypixel_server_info.votes_this_month

    colcraft_server_info = next(s for s in servers if s.server.id == server_colcraft.id)
    colcraft = colcraft_server_info.server
    colcraft_total_votes = colcraft_server_info.total_votes
    colcraft_votes_this_month = colcraft_server_info.votes_this_month

    assert hypixel
    assert hypixel_total_votes == 0
    assert hypixel_votes_this_month == 0

    assert colcraft
    assert colcraft_total_votes == 0
    assert colcraft_votes_this_month == 0


def test_get_servers_with_votes(
    session,
    server_colcraft: Server,
    server_hypixel: Server,
):
    """Tests getting servers with votes"""

    # 2 votes for colcraft
    vote_service.add_vote(
        db=session, server_id=server_colcraft.id, client_ip="192.168.0.1"
    )
    vote_service.add_vote(
        db=session, server_id=server_colcraft.id, client_ip="11.11.11.11"
    )

    # 1 vote for hypixel
    vote_service.add_vote(
        db=session, server_id=server_hypixel.id, client_ip="192.168.0.1"
    )

    servers_info: GetServersInfo = server_service.get_servers(
        db=session,
    )

    servers = servers_info.servers

    assert len(servers) == 2

    hypixel_server = next(s for s in servers if s.server.id == server_hypixel.id)
    colcraft_server = next(s for s in servers if s.server.id == server_colcraft.id)

    assert hypixel_server.server
    assert hypixel_server.votes_this_month == 1
    assert hypixel_server.total_votes == 1

    assert colcraft_server.server
    assert colcraft_server.votes_this_month == 2
    assert colcraft_server.total_votes == 2


def test_get_servers_with_votes_order(
    session,
    server_colcraft: Server,
    server_hypixel: Server,
):
    """Tests getting servers with votes - order"""

    # 2 votes for colcraft
    vote_service.add_vote(
        db=session, server_id=server_colcraft.id, client_ip="192.168.0.1"
    )
    vote_service.add_vote(
        db=session, server_id=server_colcraft.id, client_ip="11.11.11.11"
    )

    servers_info: GetServersInfo = server_service.get_servers(
        db=session,
    )

    servers = servers_info.servers
    total_servers = servers_info.total_servers

    assert len(servers) == 2
    assert total_servers == 2

    # colcraft should be first as it has the most votes
    assert servers[0].server.id == server_colcraft.id

    # now gives 3 votes to hypixel
    vote_service.add_vote(
        db=session,
        server_id=server_hypixel.id,
        client_ip="192.168.0.1",
    )
    vote_service.add_vote(
        db=session,
        server_id=server_hypixel.id,
        client_ip="192.168.0.2",
    )
    vote_service.add_vote(
        db=session,
        server_id=server_hypixel.id,
        client_ip="192.168.0.3",
    )

    servers_info: GetServersInfo = server_service.get_servers(
        db=session,
    )

    servers = servers_info.servers
    total_servers = servers_info.total_servers

    assert len(servers) == 2
    assert total_servers == 2

    # hypixel should be first as it has the most votes
    assert servers[0].server.id == server_hypixel.id


def test_get_servers_with_votes_monthly(
    session,
    server_colcraft: Server,
    votes_colcraft_20_last_month,
    votes_colcraft_20_this_month,
):
    """Tests getting servers with votes that are monthly"""

    servers_info: GetServersInfo = server_service.get_servers(
        db=session,
    )

    servers = servers_info.servers
    total_servers = servers_info.total_servers

    assert len(servers) == 1
    assert total_servers == 1

    colcraft_server = next(s for s in servers if s.server.id == server_colcraft.id)

    assert colcraft_server
    # total votes
    assert colcraft_server.total_votes == 40
    # votes this month
    assert colcraft_server.votes_this_month == 20


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
        db=session,
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
        gameplay=["Survival", "Creative", "Skyblock"],
    )

    assert server
    assert server.id
    assert server.name == "My Server"

    assert session.query(Server).count() == 1


@pytest.mark.skip(reason="Temporarily disabled")
def test_10_servers_per_user(
    session,
    user_jack: User,
):
    """Test that only one server can be created per user"""

    # create 10 servers for jack
    for i in range(1, 11):
        # create a new server for the user
        server = server_service.create_server(
            db=session,
            name=f"My Server {i}",
            user_id=user_jack.id,
            description="My Server Description",
            java_ip_address=f"1.2.3.{i}",
            java_port=8080,
            country_code="GB",
            minecraft_version="1.16.5",
            votifier_ip_address=None,
            votifier_port=None,
            votifier_key=None,
            website="https://www.myserver.com",
            discord="https://discord.gg/myserver",
            gameplay=["Survival", "Creative", "Skyblock"],
        )

    with pytest.raises(BadRequest) as e:
        server = server_service.create_server(
            db=session,
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
            gameplay=["Survival", "Creative", "Skyblock"],
        )

    assert str(e.value) == "You cannot create more than 10 servers"


def _create_multiple_servers_for_pagination(session):
    """Creates multiple servers for testing pagination"""

    for i in range(1, 35):
        # create a new user
        user = user_service.add_user(
            db=session,
            user_id=uuid4(),
            username=f"test user {i}",
            email=f"testuser{i}@gmail.com",
        )

        # create a new server for the user
        server = server_service.create_server(
            db=session,
            name=f"My Server {i}",
            user_id=user.id,
            description="My Server Description",
            java_ip_address=f"1.2.3.{i}",
            java_port=8080,
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
        get_servers_info: GetServersInfo = server_service.get_servers(
            db=session, page=page, page_size=per_page
        )

        servers = get_servers_info.servers

        for i, server_info in enumerate(servers):
            assert (
                server_info.server.name
                == f"My Server {get_servers_info.total_servers - ((page - 1) * per_page + i)}"
            )


def test_update_server_all_properties(
    session,
    user_jack: User,
    server_colcraft: Server,
):
    """Tests updating all properties on a server"""

    updated_server = server_service.update_server(
        db=session,
        server_id=server_colcraft.id,
        user_id=user_jack.id,
        name="UPDATED NAME",
        description="UPDATED DESCRIPTION",
        java_ip_address="0.0.0.0",
        java_port=9999,
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
    assert updated_server.java_ip_address == "0.0.0.0"
    assert updated_server.java_port == 9999
    assert updated_server.country_code == "FR"
    assert updated_server.minecraft_version == "9.9.9"
    assert updated_server.votifier_ip_address == "0.0.0.0"
    assert updated_server.votifier_port == 9999
    assert updated_server.votifier_key == "UPDATED KEY"
    assert updated_server.website == "https://www.updated.com"
    assert updated_server.discord == "https://discord.gg/updated"
    assert updated_server.banner_checksum is None
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
        db=session,
        name="My Server",
        user_id=user_jack.id,
        description="My Server Description",
        java_ip_address="0.0.0.0",
        java_port=1234,
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
        db=session,
        server_id=server.id,
        user_id=user_jack.id,
        name="UPDATED NAME",
        description="UPDATED DESCRIPTION",
    )

    assert updated_server
    assert updated_server.name == "UPDATED NAME"
    assert updated_server.description == "UPDATED DESCRIPTION"
    assert updated_server.java_ip_address == "0.0.0.0"
    assert updated_server.java_port == 1234
    assert updated_server.country_code == "GB"
    assert updated_server.minecraft_version == "1.16.5"
    assert updated_server.votifier_ip_address is None
    assert updated_server.votifier_port is None
    assert updated_server.votifier_key is None
    assert updated_server.website == "https://www.myserver.com"
    assert updated_server.discord == "https://discord.gg/myserver"
    assert updated_server.banner_checksum is None


def test_update_server_not_owned(
    session,
    user_jack: User,
    server_hypixel: Server,
):
    """Test for failure on updating a server that is not owned by the user"""

    with pytest.raises(Exception) as e:
        updated_server = server_service.update_server(
            db=session,
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

    assert server_colcraft.flagged_for_deletion == False

    deleted_server_id = server_service.delete_server(
        db=session,
        server_id=server_colcraft.id,
        user_id=user_jack.id,
    )

    assert deleted_server_id == server_colcraft.id
    assert session.query(Server).count() == 1
    assert (
        session.query(Server)
        .filter(Server.id == server_colcraft.id)
        .one()
        .flagged_for_deletion
    )


def test_delete_server_not_owned(
    session,
    user_jack: User,
    server_hypixel: Server,
):
    """Test for failure on deleting a server that is not owned by the user"""

    with pytest.raises(Exception) as e:
        deleted_server_id = server_service.delete_server(
            db=session,
            server_id=server_hypixel.id,
            user_id=user_jack.id,
        )

    assert str(e.value) == "You do not own this server"


def test_get_server(session, server_colcraft: Server):
    """Tests getting a server"""

    server_info: GetServerInfo = server_service.get_server(
        db=session,
        server_id=server_colcraft.id,
    )

    server = server_info.server

    assert server
    assert server.id == server_colcraft.id
    assert server.name == server_colcraft.name
    assert server_info.total_votes == 0
    assert server_info.votes_this_month == 0
    assert server_info.rank == 1


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
        db=session,
        name="My Server 2",
        user_id=user_jack.id,
        description="My Server Description",
        java_ip_address="1.2.3.4",
        gameplay=["Survival", "Creative", "Skyblock"],
        country_code="GB",
        minecraft_version="1.16.5",
    )

    # get all servers
    servers_info: GetServersInfo = server_service.get_servers(
        db=session,
    )

    servers = servers_info.servers

    assert len(servers) == 3

    # get my servers
    my_servers: list[GetServerInfo] = server_service.get_my_servers(
        db=session,
        user_id=user_jack.id,
    )

    assert len(my_servers) == 2

    for s in my_servers:
        assert s.server.id in [server_colcraft.id, server_2.id]

    # get my servers for alan
    my_servers: list[GetServerInfo] = server_service.get_my_servers(
        db=session, user_id=user_alan.id
    )

    for s in my_servers:
        assert s.server.id in [server_hypixel.id]


def test_get_server_deleted(session, server_colcraft: Server):
    """Tests getting a server that has been flagged for deletion"""

    server_service.delete_server(
        db=session,
        server_id=server_colcraft.id,
        user_id=server_colcraft.user_id,
    )

    with pytest.raises(NotFound):
        server_service.get_server(db=session, server_id=server_colcraft.id)


def test_get_servers_deleted(
    session,
    server_colcraft: Server,
    server_colcraft_2: Server,
    server_hypixel: Server,
):
    """Tests getting servers that have been flagged for deletion"""

    servers_info: GetServersInfo = server_service.get_servers(
        db=session,
    )

    servers = servers_info.servers
    total_servers = servers_info.total_servers

    assert len(servers) == 3
    assert total_servers == 3

    server_service.delete_server(
        db=session,
        server_id=server_colcraft.id,
        user_id=server_colcraft.user_id,
    )

    server_service.delete_server(
        db=session,
        server_id=server_hypixel.id,
        user_id=server_hypixel.user_id,
    )

    servers_info: GetServersInfo = server_service.get_servers(
        db=session,
    )

    assert len(servers_info.servers) == 1
    assert servers_info.total_servers == 1

    assert servers_info.servers[0].server.id == server_colcraft_2.id


def test_get_my_servers_deleted(
    session,
    server_colcraft: Server,
    server_colcraft_2: Server,
):
    """Tests getting my servers that have been flagged for deletion"""

    my_servers: list[GetServerInfo] = server_service.get_my_servers(
        db=session,
        user_id=server_colcraft.user_id,
    )

    assert len(my_servers) == 2

    server_service.delete_server(
        db=session,
        server_id=server_colcraft.id,
        user_id=server_colcraft.user_id,
    )

    my_servers: list[GetServerInfo] = server_service.get_my_servers(
        db=session,
        user_id=server_colcraft.user_id,
    )

    assert len(my_servers) == 1
    assert my_servers[0].server.id == server_colcraft_2.id


def test_get_server_rank(
    session,
    server_colcraft: Server,
    server_hypixel: Server,
    server_colcraft_2: Server,
):
    """Tests getting a server rank"""

    for i in range(1, 5):
        vote_service.add_vote(
            db=session,
            server_id=server_colcraft.id,
            client_ip=f"127.0.0.{i}",
        )

    for i in range(1, 3):
        vote_service.add_vote(
            db=session,
            server_id=server_hypixel.id,
            client_ip=f"127.0.0.{i}",
        )

    for i in range(1, 2):
        vote_service.add_vote(
            db=session,
            server_id=server_colcraft_2.id,
            client_ip=f"127.0.0.{i}",
        )

    colcraft_rank = server_service.get_server_rank(
        db=session,
        server=server_colcraft,
    )

    colcraft_2_rank = server_service.get_server_rank(
        db=session,
        server=server_colcraft_2,
    )

    hypixel_rank = server_service.get_server_rank(
        db=session,
        server=server_hypixel,
    )

    servers_info: GetServersInfo = server_service.get_servers(
        db=session,
    )

    servers = servers_info.servers

    assert colcraft_rank == 1
    assert hypixel_rank == 2
    assert colcraft_2_rank == 3

    # assert the rank is the same from the get_servers response
    assert colcraft_rank == servers[0].rank
    assert hypixel_rank == servers[1].rank
    assert colcraft_2_rank == servers[2].rank


def test_get_server_history_by_hour(
    session,
    server_colcraft: Server,
    server_colcraft_history,
):
    """Tests getting a server's historical data"""

    server_history = server_service.get_server_history(
        db=session,
        server_id=server_colcraft.id,
        time_interval="hour",
    )

    # TODO: Finish this test
    print(1)


def test_get_server_history_by_day(
    session,
    server_colcraft: Server,
    server_colcraft_history,
):
    """Tests getting a server's historical data"""

    server_history = server_service.get_server_history(
        db=session,
        server_id=server_colcraft.id,
        time_interval="day",
    )

    # TODO: Finish this test
    print(1)


def test_servers_search_query(
    session,
    server_colcraft: Server,
    server_colcraft_2: Server,
    server_hypixel: Server,
):
    """Tests the servers search query"""

    get_servers_no_search = server_service.get_servers(
        db=session,
    )

    assert len(get_servers_no_search.servers) == 3
    assert get_servers_no_search.total_servers == 3

    get_servers_search = server_service.get_servers(
        db=session,
        search_query="colcraft",
    )

    assert len(get_servers_search.servers) == 2
    assert get_servers_search.total_servers == 2
