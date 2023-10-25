from uuid import uuid4

import pytest
import freezegun
from datetime import datetime, timedelta

from msc.models import User, ServerHistory, Server
from msc.services import server_service, user_service, vote_service


@pytest.fixture
def server_colcraft(session, user_jack: User):
    """Returns a server with default values"""

    with open("tests/resources/test_image_base64_string.txt", "r") as f:
        image_base64_string = f.read()

    server = server_service.create_server(
        db=session,
        name="Colcraft server",
        user_id=user_jack.id,
        description="Here is a decription with lots of useful,info we can search upon this",
        java_ip_address="192.168.1.100",
        java_port=8080,
        country_code="GB",
        votifier_ip_address=None,
        votifier_port=None,
        votifier_key=None,
        website="https://www.myserver.com",
        discord="https://discord.gg/myserver",
        banner_base64=image_base64_string,
        tags=["survival", "pve", "tekkit", "mcmmo"],
    )

    return server


@pytest.fixture
def server_colcraft_2(session, user_jack: User):
    """Returns a server with default values"""

    with open("tests/resources/test_image_base64_string.txt", "r") as f:
        image_base64_string = f.read()

    server = server_service.create_server(
        db=session,
        name="my second server",
        user_id=user_jack.id,
        description="This is colcrafts second server",
        java_ip_address="192.168.1.100",
        java_port=8080,
        country_code="GB",
        votifier_ip_address=None,
        votifier_port=None,
        votifier_key=None,
        website="https://www.myserver.com",
        discord="https://discord.gg/myserver",
        banner_base64=image_base64_string,
        tags=["survival", "pve", "pvp", "skyblock"],
    )

    return server


@pytest.fixture
def server_hypixel(session, user_alan: User):
    """Returns a server with default values"""

    with open("tests/resources/test_image_base64_string.txt", "r") as f:
        image_base64_string = f.read()

    server = server_service.create_server(
        db=session,
        name="Hypixel",
        user_id=user_alan.id,
        description="Hypixel Description",
        java_ip_address="192.168.1.100",
        java_port=8080,
        country_code="GB",
        votifier_ip_address=None,
        votifier_port=None,
        votifier_key=None,
        website="https://www.myserver.com",
        discord="https://discord.gg/myserver",
        banner_base64=image_base64_string,
        tags=["creative", "pvp", "skyblock", "minigames"],
    )

    return server


@pytest.fixture
def ten_servers(session):
    """Returns ten servers and users"""

    output = {
        "servers_list": [],
        "users_list": [],
        "servers_map": {},
        "users_map": {},
    }

    for i in range(1, 11):
        user = user_service.add_user(
            db=session,
            user_id=uuid4(),
            username=f"User {i}",
            email=f"user{i}@gmail.com",
        )

        server = server_service.create_server(
            db=session,
            name=f"Server {i}",
            user_id=user.id,
            description="My Server Description",
            java_ip_address=f"{i}.168.1.100",
            java_port=8080,
            country_code="GB",
            tags=["Survival", "Creative", "Skyblock"],
        )

        output["servers_list"].append(server)
        output["users_list"].append(user)
        output["servers_map"][server.id] = server
        output["users_map"][user.id] = user

    return output


@pytest.fixture
def ten_more_servers(session):
    """Returns ten servers and users"""

    output = {
        "servers_list": [],
        "users_list": [],
        "servers_map": {},
        "users_map": {},
    }

    for i in range(11, 21):
        user = user_service.add_user(
            db=session,
            user_id=uuid4(),
            username=f"User {i}",
            email=f"user{i}@gmail.com",
        )

        server = server_service.create_server(
            db=session,
            name=f"Server {i}",
            user_id=user.id,
            description="My Server Description",
            java_ip_address=f"{i}.168.1.100",
            java_port=8080,
            country_code="GB",
            tags=["Survival", "Creative", "Skyblock"],
        )

        output["servers_list"].append(server)
        output["users_list"].append(user)
        output["servers_map"][server.id] = server
        output["users_map"][user.id] = user

    return output


@pytest.fixture
def many_servers(session):
    """Returns many servers"""

    output = {
        "servers_list": [],
        "users_list": [],
        "servers_map": {},
        "users_map": {},
    }

    for i in range(1, 100):
        user = user_service.add_user(
            db=session,
            user_id=uuid4(),
            username=f"User {i}",
            email=f"user{i}@gmail.com",
        )

        server = server_service.create_server(
            db=session,
            name=f"Server {i}",
            user_id=user.id,
            description="My Server Description",
            java_ip_address=f"{i}.168.1.100",
            java_port=8080,
            country_code="GB",
            tags=["Survival", "Creative", "Skyblock"],
        )

        output["servers_list"].append(server)
        output["users_list"].append(user)
        output["servers_map"][server.id] = server
        output["users_map"][user.id] = user

    return output


@pytest.fixture
def server_colcraft_history(
    session,
    server_colcraft: Server,
):
    """Creates a set of historical data points for the server colcraft

    5 days one data point per hour"""

    now = datetime.utcnow()
    five_days_ago = now - timedelta(days=5)

    for days in range(1, 5):
        for hours in range(1, 24):
            with freezegun.freeze_time(
                five_days_ago + timedelta(days=days, hours=hours)
            ):
                is_online = hours % 12 != 0
                players = days * (hours % 5)
                rank = days % 5
                uptime = 100 - days

                for i in range(0, rank):
                    vote_service.add_vote(
                        db=session,
                        server_id=server_colcraft.id,
                        client_ip=str(uuid4()),
                        minecraft_username=str(uuid4()),
                    )

                data_point = ServerHistory(
                    server_id=server_colcraft.id,
                    is_online=is_online,
                    players=players,
                    rank=rank,
                    uptime=uptime,
                    new_votes=vote_service.get_new_votes(
                        db=session,
                        server=server_colcraft,
                    ),
                    total_votes=vote_service.get_total_votes(
                        db=session,
                        server=server_colcraft,
                    ),
                    votes_this_month=vote_service.get_votes_this_month(
                        db=session,
                        server=server_colcraft,
                    ),
                )

                session.add(data_point)
                session.commit()
