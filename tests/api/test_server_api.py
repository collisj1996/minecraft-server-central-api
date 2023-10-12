from fastapi.testclient import TestClient

from msc.config import config
from msc.models import Server, User
from msc.services import server_service

from .utils import get_auth_header, get_response_body


def test_get_my_servers(
    session,
    test_client: TestClient,
    user_jack: User,
    server_colcraft: Server,
):
    config.development_mode = True
    response = test_client.get(
        "/servers/mine",
        headers=get_auth_header(user_jack.id),
    )
    assert response.status_code == 200


def test_get_my_servers_no_auth(
    session,
    test_client: TestClient,
    user_jack: User,
    server_colcraft: Server,
):
    config.development_mode = True
    response = test_client.get(
        "/servers/mine",
    )
    assert response.status_code == 401


def test_create_server_validation_only_java_ip_address(
    session,
    test_client: TestClient,
    user_jack: User,
):
    """Tests that the IP address validation works correctly"""
    config.development_mode = True
    response = test_client.post(
        "/servers",
        json={
            "name": "Test Server",
            "description": "Welcome to our Minecraft test server! Dive into an exciting world of challenges and adventures. Join us now for a unique gaming experience where you can put your skills to ",
            "java_ip_address": "1.2.3.4",
            "bedrock_port": 19132,
            "country_code": "US",
            "gameplay": ["survival", "creative", "skyblock"],
        },
        headers=get_auth_header(user_jack.id),
    )

    assert response.status_code == 200


def test_create_server_validation_only_bedrock_ip_address(
    session,
    test_client: TestClient,
    user_jack: User,
):
    """Tests that the IP address validation works correctly"""
    config.development_mode = True
    response = test_client.post(
        "/servers",
        json={
            "name": "Test Server",
            "description": "Welcome to our Minecraft test server! Dive into an exciting world of challenges and adventures. Join us now for a unique gaming experience where you can put your skills to ",
            "bedrock_ip_address": "1.2.3.4",
            "country_code": "US",
            "gameplay": ["survival", "creative", "skyblock"],
        },
        headers=get_auth_header(user_jack.id),
    )

    assert response.status_code == 200


def test_create_server_validation_both_ip_address(
    session,
    test_client: TestClient,
    user_jack: User,
):
    """Tests that the IP address validation works correctly"""
    config.development_mode = True
    response = test_client.post(
        "/servers",
        json={
            "name": "Test Server",
            "description": "Welcome to our Minecraft test server! Dive into an exciting world of challenges and adventures. Join us now for a unique gaming experience where you can put your skills to ",
            "bedrock_ip_address": "1.2.3.4",
            "java_ip_address": "1.2.3.4",
            "country_code": "US",
            "gameplay": ["survival", "creative", "skyblock"],
        },
        headers=get_auth_header(user_jack.id),
    )

    assert response.status_code == 200


def test_create_server_validation_no_ip_address(
    session,
    test_client: TestClient,
    user_jack: User,
):
    """Tests that the IP address validation works correctly"""
    config.development_mode = True
    response = test_client.post(
        "/servers",
        json={
            "name": "Test Server",
            "description": "Welcome to our Minecraft test server! Dive into an exciting world of challenges and adventures. Join us now for a unique gaming experience where you can put your skills to ",
            "country_code": "US",
            "gameplay": ["survival", "creative", "skyblock"],
        },
        headers=get_auth_header(user_jack.id),
    )

    assert response.status_code == 400
    assert get_response_body(response)["type"] == "validation_error"
    assert (
        "At least one of java_ip_address or bedrock_ip_address must be set"
        in get_response_body(response)["message"]
    )


def test_create_server_validation_name_length(
    session,
    test_client: TestClient,
    user_jack: User,
):
    """Tests that the name length validation works correctly"""

    # Test that a name less than 5 characters is too short
    config.development_mode = True
    response = test_client.post(
        "/servers",
        json={
            "name": "Four",
            "description": "Welcome to our Minecraft test server! Dive into an exciting world of challenges and adventures. Join us now for a unique gaming experience where you can put your skills to ",
            "java_ip_address": "1.2.3.4",
            "bedrock_port": 19132,
            "country_code": "US",
            "gameplay": ["survival", "creative", "skyblock"],
        },
        headers=get_auth_header(user_jack.id),
    )

    assert response.status_code == 400
    assert get_response_body(response)["type"] == "validation_error"
    assert (
        "ensure this value has at least 5 characters"
        in get_response_body(response)["message"]
    )

    # Test that a name more than 65 characters is too long
    response = test_client.post(
        "/servers",
        json={
            "name": "asdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdf",
            "description": "Welcome to our Minecraft test server! Dive into an exciting world of challenges and adventures. Join us now for a unique gaming experience where you can put your skills to ",
            "java_ip_address": "1.2.3.4",
            "bedrock_port": 19132,
            "country_code": "US",
            "gameplay": ["survival", "creative", "skyblock"],
        },
        headers=get_auth_header(user_jack.id),
    )

    assert response.status_code == 400
    assert get_response_body(response)["type"] == "validation_error"
    assert (
        "ensure this value has at most 65 characters"
        in get_response_body(response)["message"]
    )


def test_create_server_validation_description_length(
    session,
    test_client: TestClient,
    user_jack: User,
):
    """Tests that the description length validation works correctly"""

    # Test that a description less than 150 characters is too short
    config.development_mode = True
    response = test_client.post(
        "/servers",
        json={
            "name": "Fourasdasd",
            "description": "Welcome to our Minecraft test server! Dive into an exciting world of challenges and adventures. Join us now for a unique gaming",
            "java_ip_address": "1.2.3.4",
            "bedrock_port": 19132,
            "country_code": "US",
            "gameplay": ["survival", "creative", "skyblock"],
        },
        headers=get_auth_header(user_jack.id),
    )

    assert response.status_code == 400
    body = get_response_body(response)
    assert body["type"] == "validation_error"
    assert "ensure this value has at least 150 characters" in body["message"]

    # Test that a name more than 65 characters is too long
    response = test_client.post(
        "/servers",
        json={
            "name": "asdasdasdadadadskdfjgbsdfkjbsdkj",
            "description": "asdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdfasdasdasdadadadskdfjgbsdfkjbsdkjnsdcjnsdkjbsdgjkbsdfkjbsdfjkbsdfdf",
            "java_ip_address": "1.2.3.4",
            "bedrock_port": 19132,
            "country_code": "US",
            "gameplay": ["survival", "creative", "skyblock"],
        },
        headers=get_auth_header(user_jack.id),
    )

    assert response.status_code == 400
    assert get_response_body(response)["type"] == "validation_error"
    assert (
        "ensure this value has at most 1500 characters"
        in get_response_body(response)["message"]
    )


def test_update_server_validation_no_ip_address(
    session,
    test_client: TestClient,
    user_jack: User,
    server_colcraft: Server,
):
    """Tests ip validation when updating a server to have no java or bedrock IP address"""

    config.development_mode = True

    response = test_client.patch(
        f"/servers/{str(server_colcraft.id)}",
        json={
            "java_ip_address": None,
            "bedrock_ip_address": "1.2.3.4",
        },
        headers=get_auth_header(user_jack.id),
    )
    assert response.status_code == 200

    response = test_client.patch(
        f"/servers/{str(server_colcraft.id)}",
        json={
            "java_ip_address": "1.2.3.4",
            "bedrock_ip_address": None,
        },
        headers=get_auth_header(user_jack.id),
    )
    assert response.status_code == 200

    response = test_client.patch(
        f"/servers/{str(server_colcraft.id)}",
        json={
            "java_ip_address": "1.2.3.4",
            "bedrock_ip_address": "1.2.3.4",
        },
        headers=get_auth_header(user_jack.id),
    )
    assert response.status_code == 200

    response = test_client.patch(
        f"/servers/{str(server_colcraft.id)}",
        json={
            "java_ip_address": None,
            "bedrock_ip_address": None,
        },
        headers=get_auth_header(user_jack.id),
    )

    assert response.status_code == 400
    assert get_response_body(response)["type"] == "validation_error"
    assert (
        "At least one of java_ip_address or bedrock_ip_address must be set"
        in get_response_body(response)["message"]
    )


def test_server_test_votifier(
    session,
    user_jack: User,
    test_client: TestClient,
    mocker,
):
    """Test the Test Votifier endpoint"""

    config.development_mode = True

    mocker.patch("msc.utils.api_utils.get_client_ip", return_value="testclient")

    # create a server
    server = server_service.create_server(
        db=session,
        name="Test Local Server",
        description="This is my actual local test server it is hosted on my PC and I will use it to test that votifier works and for other test purposes... adslnasdlajsndlasdlknasdklnaslkdnalksndklansd",
        user_id=user_jack.id,
        country_code="US",
        java_ip_address="5.71.159.170",
        java_port=25565,
        gameplay=["survival", "creative", "skyblock"],
        use_votifier=True,
        votifier_ip_address="5.71.159.170",
        votifier_port=8192,
        votifier_key="o4c1en9ug4639t8foddt32sibb",
    )

    # call the test votifier endpoint

    response = test_client.post(
        f"/servers/{str(server.id)}/test_votifier",
        headers=get_auth_header(user_jack.id),
        json={
            "minecraft_username": "mcsc_test_user",
        },
    )

    assert response.status_code == 200
