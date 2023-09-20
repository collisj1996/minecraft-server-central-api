import requests
from uuid import uuid4
import pytest

@pytest.mark.skip(reason="This test is for a temporary script")
def test_temp_script(session):

    users_endpoint = "https://api.minecraftservercentral.com/users"
    servers_endpoint = "https://api.minecraftservercentral.com/servers"

    # create 100 servers each with a unique user and server name
    for i in range(100):
        user_id = str(uuid4())

        user_payload = {
            "user_id": user_id,
            "username": f"User {i}",
            "email": f"user{i}@gmail.com",
        }

        server_payload = {
            "name": f"Server {i}",
            "description": f"A great server number {i}",
            "ip_address": f"1.2.3.{i}",
            "port": 25565,
            "country_code": "GB",
            "minecraft_version": "1.16.5",
            "website": "https://www.minecraftservercentral.com",
            "discord": "https://discord.gg/msc",
        }

        # create the user
        user_response = requests.post(users_endpoint, json=user_payload)

        assert user_response.status_code == 200

        # create the server
        server_response = requests.post(servers_endpoint, json=server_payload, headers={"msc-user-id": user_id})

        assert server_response.status_code == 200