from uuid import uuid4

import pytest
import freezegun
from datetime import datetime, timedelta

from msc.models import User, ServerHistory, Server
from msc.services import server_service, user_service


@pytest.fixture
def server_colcraft(session, user_jack: User):
    """Returns a server with default values"""

    with open("tests/resources/test_image_base64_string.txt", "r") as f:
        image_base64_string = f.read()

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
        banner_base64=image_base64_string,
        gameplay=["Survival", "Creative", "Skyblock"],
    )

    return server


@pytest.fixture
def server_colcraft_2(session, user_jack: User):
    """Returns a server with default values"""

    with open("tests/resources/test_image_base64_string.txt", "r") as f:
        image_base64_string = f.read()

    server = server_service.create_server(
        db=session,
        name="My Server 2",
        user_id=user_jack.id,
        description="My Server Description 2",
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
            minecraft_version="1.16.5",
            gameplay=["Survival", "Creative", "Skyblock"],
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
            minecraft_version="1.16.5",
            gameplay=["Survival", "Creative", "Skyblock"],
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

    for days in range(1, 5):
        for hours in range(1, 24):
            with freezegun.freeze_time(
                datetime.utcnow() - timedelta(days=days, hours=hours)
            ):
                is_online = hours % 12 != 0
                players = days * (hours % 5)
                rank = days % 5
                uptime = 100 - days

                data_point = ServerHistory(
                    server_id=server_colcraft.id,
                    is_online=is_online,
                    players=players,
                    rank=rank,
                    uptime=uptime,
                )

                session.add(data_point)
    session.commit()
