from msc.jobs.tasks import poll_java_server, poll_bedrock_server, _upload_server_icon
from msc.models import User, Server
from msc.services import server_service
from mcstatus.status_response import (
    JavaStatusResponse,
    BedrockStatusResponse,
    BedrockStatusPlayers,
    BedrockStatusVersion,
    JavaStatusPlayers,
    JavaStatusPlayer,
    JavaStatusVersion,
)
from mcstatus.querier import QueryResponse
from socket import gaierror


def test_poll_java_server_no_query(
    session,
    user_jack: User,
    mocker,
):
    """Test poll java server function"""

    # create a new server with no polled stats
    server_colcraft = server_service.create_server(
        name="ColCraft",
        user_id=user_jack.id,
        country_code="US",
        minecraft_version="1.17.1",
        gameplay=["survival", "creative", "skyblock"],
        description="A test server",
        java_ip_address="1.2.3.4",
        java_port=25565,
    )

    # confirm server has no polled stats
    server: Server = (
        session.query(Server)
        .filter(
            Server.id == server_colcraft.id,
        )
        .one_or_none()
    )

    assert server.is_online is False
    assert server.players == 0
    assert server.max_players == 0
    assert server.icon_checksum is None

    # load test icon
    with open("tests/resources/test_icon_base64_string.txt", "r") as file:
        image_base64_string = file.read()

    mocked_status_response = JavaStatusResponse(
        version=JavaStatusVersion(
            name="1.17.1",
            protocol=755,
        ),
        players=JavaStatusPlayers(
            max=20,
            online=10,
            sample=[
                JavaStatusPlayer(
                    id="12345678-1234-1234-1234-123456789abc",
                    name="test",
                ),
            ],
        ),
        motd=None,
        icon=image_base64_string,
        latency=0,
        raw=None,
    )

    # mock java server status and query
    mocker.patch(
        "msc.jobs.tasks.JavaServer.status", return_value=mocked_status_response
    )

    # poll server
    poll_java_server(server=server_colcraft)

    # confirm server has polled stats
    server: Server = (
        session.query(Server)
        .filter(
            Server.id == server_colcraft.id,
        )
        .one_or_none()
    )

    assert server.is_online is True
    assert server.players == 10
    assert server.max_players == 20
    assert server.icon_checksum == "1b28f993c9d2852b501e852d90a3e36b"


def test_poll_java_server_with_query(
    session,
    user_jack: User,
    mocker,
):
    """Test poll java server function"""

    # create a new server with no polled stats
    server_colcraft = server_service.create_server(
        name="ColCraft",
        user_id=user_jack.id,
        country_code="US",
        minecraft_version="1.17.1",
        gameplay=["survival", "creative", "skyblock"],
        description="A test server",
        java_ip_address="1.2.3.4",
        java_port=25565,
    )

    # confirm server has no polled stats
    server: Server = (
        session.query(Server)
        .filter(
            Server.id == server_colcraft.id,
        )
        .one_or_none()
    )

    assert server.is_online is False
    assert server.players == 0
    assert server.max_players == 0
    assert server.icon_checksum is None

    # mocked query response
    mocked_query_response = QueryResponse(
        players=QueryResponse.Players(
            max=20,
            online=10,
            names=[
                "test",
            ],
        ),
        raw={
            "hostname": "ColCraft",
            "map": "world",
            "numplayers": "10",
            "maxplayers": "20",
            "version": "1.17.1",
            "plugins": "",
        },
    )

    # mock java server status and query
    mocker.patch(
        "msc.jobs.tasks.JavaServer.status",
        side_effect=TimeoutError,
    )

    mocker.patch(
        "msc.jobs.tasks.JavaServer.query",
        return_value=mocked_query_response,
    )

    # poll server
    poll_java_server(server=server_colcraft)

    # confirm server has polled stats (NO ICON CHECKSUM)
    server: Server = (
        session.query(Server)
        .filter(
            Server.id == server_colcraft.id,
        )
        .one_or_none()
    )

    assert server.is_online is True
    assert server.players == 10
    assert server.max_players == 20
    assert server.icon_checksum is None


def test_poll_bedrock_server(session, user_jack: User, mocker):
    # create a new server with no polled stats
    server_colcraft = server_service.create_server(
        name="ColCraft",
        user_id=user_jack.id,
        country_code="US",
        minecraft_version="1.17.1",
        gameplay=["survival", "creative", "skyblock"],
        description="A test server",
        bedrock_ip_address="1.2.3.4",
    )

    # confirm server has no polled stats
    server: Server = (
        session.query(Server)
        .filter(
            Server.id == server_colcraft.id,
        )
        .one_or_none()
    )

    assert server.is_online is False
    assert server.players == 0
    assert server.max_players == 0
    assert server.icon_checksum is None

    mocked_bedrock_status_response = BedrockStatusResponse(
        version=BedrockStatusVersion(
            name="1.17.1",
            brand="MCPE",
            protocol=755,
        ),
        players=BedrockStatusPlayers(
            max=20,
            online=10,
        ),
        motd=None,
        latency=0,
        map_name="world",
        gamemode="survival",
    )

    # mock bedrock server status
    mocker.patch(
        "msc.jobs.tasks.BedrockServer.status",
        return_value=mocked_bedrock_status_response,
    )

    # poll server
    poll_bedrock_server(server=server_colcraft)

    # confirm server has polled stats
    server: Server = (
        session.query(Server)
        .filter(
            Server.id == server_colcraft.id,
        )
        .one_or_none()
    )

    assert server.is_online is True
    assert server.players == 10
    assert server.max_players == 20
    assert server.icon_checksum is None


def test_poll_java_server_go_offline(session, user_jack: User, mocker):
    # create a new server with no polled stats
    server_colcraft = server_service.create_server(
        name="ColCraft",
        user_id=user_jack.id,
        country_code="US",
        minecraft_version="1.17.1",
        gameplay=["survival", "creative", "skyblock"],
        description="A test server",
        java_ip_address="1.2.3.4",
        java_port=25565,
    )

    # add some dummy stats
    server_colcraft.is_online = True
    server_colcraft.players = 10
    server_colcraft.max_players = 20

    # commit changes
    session.commit()

    # mock java server status and query with TimeoutError
    mocker.patch(
        "msc.jobs.tasks.JavaServer.status",
        side_effect=TimeoutError,
    )

    mocker.patch(
        "msc.jobs.tasks.JavaServer.query",
        side_effect=TimeoutError,
    )

    # poll server
    poll_java_server(server=server_colcraft)

    # confirm server has offline stats
    server: Server = (
        session.query(Server)
        .filter(
            Server.id == server_colcraft.id,
        )
        .one_or_none()
    )

    assert server.is_online is False
    assert server.players == 0
    assert server.max_players == 20


def test_bedrock_server_go_offline(session, user_jack: User, mocker):
    # create a new server with no polled stats
    server_colcraft = server_service.create_server(
        name="ColCraft",
        user_id=user_jack.id,
        country_code="US",
        minecraft_version="1.17.1",
        gameplay=["survival", "creative", "skyblock"],
        description="A test server",
        bedrock_ip_address="1.2.3.4",
    )

    # add some dummy stats
    server_colcraft.is_online = True
    server_colcraft.players = 10
    server_colcraft.max_players = 20

    # commit changes
    session.commit()

    # mock bedrock server status with TimeoutError
    mocker.patch(
        "msc.jobs.tasks.BedrockServer.status",
        side_effect=TimeoutError,
    )

    # poll server
    poll_bedrock_server(server=server_colcraft)

    # confirm server has offline stats
    server: Server = (
        session.query(Server)
        .filter(
            Server.id == server_colcraft.id,
        )
        .one_or_none()
    )

    assert server.is_online is False
    assert server.players == 0
    assert server.max_players == 20


def test_poll_java_server_invalid_ip(session, user_jack: User, mocker):
    # create a new server with no polled stats
    server_colcraft = server_service.create_server(
        name="ColCraft",
        user_id=user_jack.id,
        country_code="US",
        minecraft_version="1.17.1",
        gameplay=["survival", "creative", "skyblock"],
        description="A test server",
        java_ip_address="SILLY IP",
        java_port=25565,
    )

    # add some dummy stats
    server_colcraft.is_online = True
    server_colcraft.players = 10
    server_colcraft.max_players = 20

    # mock java server status and query with gaierror
    mocker.patch(
        "msc.jobs.tasks.JavaServer.status",
        side_effect=gaierror,
    )

    mocker.patch(
        "msc.jobs.tasks.JavaServer.query",
        side_effect=gaierror,
    )

    poll_java_server(server=server_colcraft)

    # confirm server has offline stats
    server: Server = (
        session.query(Server)
        .filter(
            Server.id == server_colcraft.id,
        )
        .one_or_none()
    )

    assert server.is_online is False
    assert server.players == 0
    assert server.max_players == 20


def test_poll_bedrock_server_invalid_ip(session, user_jack: User, mocker):
    # create a new server with no polled stats
    server_colcraft = server_service.create_server(
        name="ColCraft",
        user_id=user_jack.id,
        country_code="US",
        minecraft_version="1.17.1",
        gameplay=["survival", "creative", "skyblock"],
        description="A test server",
        bedrock_ip_address="SILLY IP",
    )

    # add some dummy stats
    server_colcraft.is_online = True
    server_colcraft.players = 10
    server_colcraft.max_players = 20

    # mock bedrock server status with gaierror
    mocker.patch(
        "msc.jobs.tasks.BedrockServer.status",
        side_effect=gaierror,
    )

    poll_bedrock_server(server=server_colcraft)

    # confirm server has offline stats
    server: Server = (
        session.query(Server)
        .filter(
            Server.id == server_colcraft.id,
        )
        .one_or_none()
    )

    assert server.is_online is False
    assert server.players == 0
    assert server.max_players == 20


def test_upload_server_icon(
    session,
):
    """Test upload server icon function"""

    with open("tests/resources/test_icon_base64_string.txt", "r") as file:
        image_base64_string = file.read()

    _upload_server_icon(
        image_base64_string,
        server_id="f2e9d9c4-6f3c-4e5e-8d7c-9f9d8e7b6c5d",
    )
