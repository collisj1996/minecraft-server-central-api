import base64
from io import BytesIO
from uuid import uuid4
import freezegun
from datetime import datetime, timedelta

import pytest

from msc.errors import BadRequest, NotFound
from msc.models import Server, User, Vote, Sponsor
from msc.services import server_service, user_service, vote_service, sponsor_service
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
    server_colcraft_2: Server,
    ten_servers,
):
    """Tests getting servers with votes"""

    # 2 votes for colcraft
    vote_service.add_vote(
        db=session,
        server_id=server_colcraft.id,
        client_ip="192.168.0.1",
        minecraft_username="test",
    )
    vote_service.add_vote(
        db=session,
        server_id=server_colcraft.id,
        client_ip="11.11.11.11",
        minecraft_username="test_2",
    )

    # 1 vote for hypixel
    vote_service.add_vote(
        db=session,
        server_id=server_hypixel.id,
        client_ip="192.168.0.1",
        minecraft_username="test",
    )

    # sponsor some serve
    sponsor_1 = Sponsor(
        user_id=ten_servers["servers_list"][0].user_id,
        server_id=ten_servers["servers_list"][0].id,
        slot=3,
        year=datetime.utcnow().year,
        month=datetime.utcnow().month,
    )

    sponsor_2 = Sponsor(
        user_id=ten_servers["servers_list"][1].user_id,
        server_id=ten_servers["servers_list"][1].id,
        slot=2,
        year=datetime.utcnow().year,
        month=datetime.utcnow().month,
    )

    # no votes for - colcraft_2 but they are a sponsor
    sponsor_3 = Sponsor(
        user_id=server_colcraft_2.user_id,
        server_id=server_colcraft_2.id,
        slot=1,
        year=datetime.utcnow().year,
        month=datetime.utcnow().month,
    )

    session.add(sponsor_1)
    session.add(sponsor_2)
    session.add(sponsor_3)
    session.commit()

    servers_info: GetServersInfo = server_service.get_servers(
        db=session,
    )

    servers = servers_info.servers

    assert len(servers) == 10

    # colcraft_2 should be first as they are a sponsor (slot 1)
    assert servers[0].server.id == server_colcraft_2.id
    assert servers[0].rank == 1

    # ten_servers["servers_list"][1].id should be second as they are a sponsor (slot 2)
    assert servers[1].server.id == ten_servers["servers_list"][1].id
    assert servers[1].rank == 2

    # ten_servers["servers_list"][0].id should be third as they are a sponsor (slot 3)
    assert servers[2].server.id == ten_servers["servers_list"][0].id
    assert servers[2].rank == 3

    # colcraft should be second as it has the most votes
    assert servers[3].server.id == server_colcraft.id
    assert servers[3].rank == 4

    # hypixel should be third as it has the least votes
    assert servers[4].server.id == server_hypixel.id
    assert servers[4].rank == 5

    assert servers[5].server
    assert servers[5].rank == 6
    assert servers[6].server
    assert servers[6].rank == 6


def test_get_servers_with_votes_order(
    session,
    server_colcraft: Server,
    server_hypixel: Server,
):
    """Tests getting servers with votes - order"""

    # 2 votes for colcraft
    vote_service.add_vote(
        db=session,
        server_id=server_colcraft.id,
        client_ip="192.168.0.1",
        minecraft_username="test",
    )
    vote_service.add_vote(
        db=session,
        server_id=server_colcraft.id,
        client_ip="11.11.11.11",
        minecraft_username="test_2",
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
        minecraft_username="test",
    )
    vote_service.add_vote(
        db=session,
        server_id=server_hypixel.id,
        client_ip="192.168.0.2",
        minecraft_username="test_2",
    )
    vote_service.add_vote(
        db=session,
        server_id=server_hypixel.id,
        client_ip="192.168.0.3",
        minecraft_username="test_3",
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
        votifier_ip_address=None,
        votifier_port=None,
        votifier_key=None,
        website="https://www.myserver.com",
        discord="https://discord.gg/myserver",
        tags=["Survival", "Creative", "Skyblock"],
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
            votifier_ip_address=None,
            votifier_port=None,
            votifier_key=None,
            website="https://www.myserver.com",
            discord="https://discord.gg/myserver",
            tags=["Survival", "Creative", "Skyblock"],
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
            votifier_ip_address=None,
            votifier_port=None,
            votifier_key=None,
            website="https://www.myserver.com",
            discord="https://discord.gg/myserver",
            tags=["Survival", "Creative", "Skyblock"],
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
            votifier_ip_address=None,
            votifier_port=None,
            votifier_key=None,
            website="https://www.myserver.com",
            discord="https://discord.gg/myserver",
            tags=["Survival", "Creative", "Skyblock"],
        )

        # force add i votes for the server
        # directly add vote to database
        for _ in range(i):
            vote = Vote(
                server_id=server.id,
                client_ip_address=f"1.2.3.{i}",
                minecraft_username=f"test{i}",
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
        votifier_ip_address="0.0.0.0",
        votifier_port=9999,
        votifier_key="UPDATED KEY",
        website="https://www.updated.com",
        discord="https://discord.gg/updated",
        banner_base64=None,
        tags=["Survival", "Creative", "Skyblock", "Bedwars", "Minigames"],
    )

    assert updated_server
    assert updated_server.name == "UPDATED NAME"
    assert updated_server.description == "UPDATED DESCRIPTION"
    assert updated_server.java_ip_address == "0.0.0.0"
    assert updated_server.java_port == 9999
    assert updated_server.country_code == "FR"
    assert updated_server.votifier_ip_address == "0.0.0.0"
    assert updated_server.votifier_port == 9999
    assert updated_server.votifier_key == "UPDATED KEY"
    assert updated_server.website == "https://www.updated.com"
    assert updated_server.discord == "https://discord.gg/updated"
    assert updated_server.banner_checksum is None
    for updated_tags in [g.name for g in updated_server.tags]:
        assert updated_tags in [
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
        votifier_ip_address=None,
        votifier_port=None,
        votifier_key=None,
        website="https://www.myserver.com",
        discord="https://discord.gg/myserver",
        tags=["Survival", "Creative", "Skyblock"],
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
        tags=["Survival", "Creative", "Skyblock"],
        country_code="GB",
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
            minecraft_username=f"test{i}",
        )

    for i in range(1, 3):
        vote_service.add_vote(
            db=session,
            server_id=server_hypixel.id,
            client_ip=f"127.0.0.{i}",
            minecraft_username=f"test{i}",
        )

    for i in range(1, 2):
        vote_service.add_vote(
            db=session,
            server_id=server_colcraft_2.id,
            client_ip=f"127.0.0.{i}",
            minecraft_username=f"test{i}",
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


def test_servers_search_query_tags(
    session,
    server_colcraft: Server,
    server_colcraft_2: Server,
    server_hypixel: Server,
):
    """Tests the servers search query"""

    get_servers_no_tags = server_service.get_servers(
        db=session,
    )

    assert len(get_servers_no_tags.servers) == 3
    assert get_servers_no_tags.total_servers == 3

    get_servers_search = server_service.get_servers(
        db=session,
        tags=["survival"],
    )

    assert len(get_servers_search.servers) == 2
    assert get_servers_search.total_servers == 2
    for server_info in get_servers_search.servers:
        assert server_info.server.id in [server_colcraft.id, server_colcraft_2.id]

    get_servers_search = server_service.get_servers(
        db=session,
        tags=["creative"],
    )

    assert len(get_servers_search.servers) == 1
    assert get_servers_search.total_servers == 1
    for server_info in get_servers_search.servers:
        assert server_info.server.id in [server_hypixel.id]


def test_servers_search_query_and_votes(
    session,
    server_colcraft: Server,
    server_colcraft_2: Server,
    server_hypixel: Server,
):
    """Tests the servers search query and votes"""

    # 5 votes for colcraft
    for i in range(1, 6):
        vote_service.add_vote(
            db=session,
            server_id=server_colcraft.id,
            client_ip=f"127.0.0.{i}",
            minecraft_username=f"test{i}",
        )

    # 2 votes for colcraft_2
    for i in range(1, 3):
        vote_service.add_vote(
            db=session,
            server_id=server_colcraft_2.id,
            client_ip=f"127.0.0.{i}",
            minecraft_username=f"test{i}",
        )

    # 1 vote for hypixel
    vote_service.add_vote(
        db=session,
        server_id=server_hypixel.id,
        client_ip="127.0.0.1",
        minecraft_username="test",
    )

    get_servers_no_search = server_service.get_servers(
        db=session,
    )

    assert len(get_servers_no_search.servers) == 3
    assert get_servers_no_search.total_servers == 3

    for server_info in get_servers_no_search.servers:
        if server_info.server.id == server_colcraft.id:
            assert server_info.total_votes == 5
        elif server_info.server.id == server_colcraft_2.id:
            assert server_info.total_votes == 2
        elif server_info.server.id == server_hypixel.id:
            assert server_info.total_votes == 1

    get_servers_search = server_service.get_servers(
        db=session,
        search_query="colcraft",
    )

    assert len(get_servers_search.servers) == 2
    assert get_servers_search.total_servers == 2

    for server_info in get_servers_search.servers:
        if server_info.server.id == server_colcraft.id:
            assert server_info.total_votes == 5
        elif server_info.server.id == server_colcraft_2.id:
            assert server_info.total_votes == 2


def test_servers_search_query_tags_and_votes(
    session,
    server_colcraft: Server,
    server_colcraft_2: Server,
    server_hypixel: Server,
):
    """"""

    # 5 votes for colcraft
    for i in range(1, 6):
        vote_service.add_vote(
            db=session,
            server_id=server_colcraft.id,
            client_ip=f"127.0.0.{i}",
            minecraft_username=f"test{i}",
        )

    # 2 votes for colcraft_2
    for i in range(1, 3):
        vote_service.add_vote(
            db=session,
            server_id=server_colcraft_2.id,
            client_ip=f"127.0.0.{i}",
            minecraft_username=f"test{i}",
        )

    # 1 vote for hypixel
    vote_service.add_vote(
        db=session,
        server_id=server_hypixel.id,
        client_ip="127.0.0.1",
        minecraft_username="test",
    )

    get_servers_no_search = server_service.get_servers(
        db=session,
    )

    assert len(get_servers_no_search.servers) == 3
    assert get_servers_no_search.total_servers == 3

    for server_info in get_servers_no_search.servers:
        if server_info.server.id == server_colcraft.id:
            assert server_info.total_votes == 5
        elif server_info.server.id == server_colcraft_2.id:
            assert server_info.total_votes == 2
        elif server_info.server.id == server_hypixel.id:
            assert server_info.total_votes == 1

    get_servers_search = server_service.get_servers(
        db=session,
        tags=["survival"],
    )

    assert len(get_servers_search.servers) == 2
    assert get_servers_search.total_servers == 2

    for server_info in get_servers_search.servers:
        if server_info.server.id == server_colcraft.id:
            assert server_info.total_votes == 5
        elif server_info.server.id == server_colcraft_2.id:
            assert server_info.total_votes == 2

    get_servers_search = server_service.get_servers(
        db=session,
        tags=["creative"],
    )

    assert len(get_servers_search.servers) == 1
    assert get_servers_search.total_servers == 1

    for server_info in get_servers_search.servers:
        if server_info.server.id == server_hypixel.id:
            assert server_info.total_votes == 1


def test_get_sponsored_servers(
    session,
    server_colcraft: Server,
    server_colcraft_2: Server,
    server_hypixel: Server,
):
    """Test getting sponsored servers"""

    with freezegun.freeze_time(datetime(2021, 12, 15)):
        # add a sponsored server
        sponsor_service._add_sponsor(
            db=session,
            user_id=server_colcraft.user_id,
            server_id=server_colcraft.id,
            sponsored_year=2021,
            sponsored_month=12,
            slot=1,
        )

        # add a sponsored server
        sponsor_service._add_sponsor(
            db=session,
            user_id=server_colcraft_2.user_id,
            server_id=server_colcraft_2.id,
            sponsored_year=2021,
            sponsored_month=12,
            slot=2,
        )

        sponsored_servers = server_service.get_sponsored_servers(
            db=session,
        )

        assert len(sponsored_servers) == 2

        # assert the sponsored servers are in the correct order
        assert sponsored_servers[0].server.id == server_colcraft.id
        assert sponsored_servers[1].server.id == server_colcraft_2.id


def test_get_sponsored_servers_scoped_to_year_and_month(
    session,
    server_colcraft: Server,
    server_colcraft_2: Server,
    server_hypixel: Server,
):
    """Tests that the get sponsored servers query is scoped to the current year and month"""

    # add some sponsored servers for 2021 10
    sponsor_service._add_sponsor(
        db=session,
        user_id=server_colcraft.user_id,
        server_id=server_colcraft.id,
        sponsored_year=2021,
        sponsored_month=10,
        slot=2,
    )

    sponsor_service._add_sponsor(
        db=session,
        user_id=server_colcraft_2.user_id,
        server_id=server_colcraft_2.id,
        sponsored_year=2021,
        sponsored_month=10,
        slot=1,
    )

    # add some sponsored servers for 2021 11
    sponsor_service._add_sponsor(
        db=session,
        user_id=server_colcraft.user_id,
        server_id=server_colcraft.id,
        sponsored_year=2021,
        sponsored_month=11,
        slot=1,
    )

    # add a sponsored server 2021 12
    sponsor_service._add_sponsor(
        db=session,
        user_id=server_colcraft.user_id,
        server_id=server_colcraft.id,
        sponsored_year=2021,
        sponsored_month=12,
        slot=3,
    )

    sponsor_service._add_sponsor(
        db=session,
        user_id=server_hypixel.user_id,
        server_id=server_hypixel.id,
        sponsored_year=2021,
        sponsored_month=12,
        slot=1,
    )

    sponsor_service._add_sponsor(
        db=session,
        user_id=server_colcraft_2.user_id,
        server_id=server_colcraft_2.id,
        sponsored_year=2021,
        sponsored_month=12,
        slot=2,
    )

    # assert all sponsored servers are in the database
    assert session.query(Sponsor).count() == 6

    # check correct sponsored servers are returned for 2021 10
    with freezegun.freeze_time(datetime(2021, 10, 15)):
        sponsored_servers = server_service.get_sponsored_servers(
            db=session,
        )

        assert len(sponsored_servers) == 2

        # assert the sponsored servers are in the correct order
        assert sponsored_servers[0].server.id == server_colcraft_2.id  # slot 1
        assert sponsored_servers[1].server.id == server_colcraft.id  # slot 2

    # check correct sponsored servers are returned for 2021 11
    with freezegun.freeze_time(datetime(2021, 11, 15)):
        sponsored_servers = server_service.get_sponsored_servers(
            db=session,
        )

        assert len(sponsored_servers) == 1

        # assert the sponsored servers are in the correct order
        assert sponsored_servers[0].server.id == server_colcraft.id  # slot 1

    # check correct sponsored servers are returned for 2021 12
    with freezegun.freeze_time(datetime(2021, 12, 15)):
        sponsored_servers = server_service.get_sponsored_servers(
            db=session,
        )

        assert len(sponsored_servers) == 3

        # assert the sponsored servers are in the correct order
        assert sponsored_servers[0].server.id == server_hypixel.id  # slot 1
        assert sponsored_servers[1].server.id == server_colcraft_2.id  # slot 2
        assert sponsored_servers[2].server.id == server_colcraft.id  # slot 3


@pytest.mark.nomockgeteligibility
def test_get_auction_eligibility(session, server_colcraft: Server):
    """Tests getting auction eligibility"""

    # set server uptime to 89%
    server_colcraft.uptime = 89
    # set created_at to 29 days ago
    server_colcraft.created_at = datetime.utcnow() - timedelta(days=29)

    session.commit()

    elegibility = server_service._get_auction_eligibility(
        server=server_colcraft,
    )
    is_eligible = server_service.is_eligible_for_auction(
        server=server_colcraft,
    )

    assert not elegibility.uptime
    assert not elegibility.server_age
    assert not is_eligible

    # set server uptime to 90%
    server_colcraft.uptime = 90
    # set created_at to 30 days ago
    server_colcraft.created_at = datetime.utcnow() - timedelta(days=30)

    session.commit()

    elegibility = server_service._get_auction_eligibility(
        server=server_colcraft,
    )
    is_eligible = server_service.is_eligible_for_auction(
        server=server_colcraft,
    )

    assert elegibility.uptime
    assert elegibility.server_age
    assert is_eligible

    # set server uptime to 91%
    server_colcraft.uptime = 91
    # set created_at to 31 days ago
    server_colcraft.created_at = datetime.utcnow() - timedelta(days=31)

    session.commit()

    elegibility = server_service._get_auction_eligibility(
        server=server_colcraft,
    )
    is_eligible = server_service.is_eligible_for_auction(
        server=server_colcraft,
    )

    assert elegibility.uptime
    assert elegibility.server_age
    assert is_eligible


def test_search_correct_rank(
    session,
    server_colcraft: Server,
    server_colcraft_2: Server,
    server_hypixel: Server,
):
    """Test that the rank remains correct when searching"""

    # add 2 votes for colcraft
    for i in range(1, 3):
        vote_service.add_vote(
            db=session,
            server_id=server_colcraft.id,
            client_ip=f"127.0.0.{i}",
            minecraft_username=f"test{i}",
        )

    # add 1 vote for colcraft_2
    vote_service.add_vote(
        db=session,
        server_id=server_colcraft_2.id,
        client_ip="127.0.0.1",
        minecraft_username="test",
    )

    # get servers
    servers = server_service.get_servers(
        db=session,
    )

    assert servers.total_servers == 3

    # assert the rank is correct
    assert servers.servers[0].server.id == server_colcraft.id
    assert servers.servers[0].rank == 1
    assert servers.servers[1].server.id == server_colcraft_2.id
    assert servers.servers[1].rank == 2
    assert servers.servers[2].server.id == server_hypixel.id
    assert servers.servers[2].rank == 3

    # search for hypixel - should be rank 3
    servers = server_service.get_servers(
        db=session,
        search_query="hypixel",
    )

    assert servers.total_servers == 1
    assert servers.servers[0].server.id == server_hypixel.id
    assert servers.servers[0].rank == 3
