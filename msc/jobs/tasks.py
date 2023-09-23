import logging
from contextlib import contextmanager
import boto3
from uuid import uuid4

from mcstatus import BedrockServer, JavaServer
from mcstatus.status_response import JavaStatusResponse, BedrockStatusResponse
from mcstatus.querier import QueryResponse

from msc import db
from msc.models import Server

logger = logging.getLogger(__name__)


@contextmanager
def _handle_db_errors():
    """Handles database errors"""
    try:
        yield
    except Exception as e:
        logger.error("Error adding server information: %s", e)
        db.session.rollback()


def _upload_server_icon(base64: str) -> str:
    """Uploads a server icon to S3 and returns the URL"""

    # Remove metadata from base64 string
    base64_data = base64.split("base64,")[1]

    # Decode the base64 image
    decoded_data = base64.b64decode(base64_data.encode() + b"==")

    s3 = boto3.client("s3")
    key = f"icons/{uuid4()}.png"

    try:
        s3.put_object(
            Body=decoded_data,
            Bucket="cdn.minecraftservercentral.com",
            Key=key,
        )
    except Exception as e:
        logger.error(f"Error uploading server icon: {e}")
        return None

    return f"https://cdn.minecraftservercentral.com/{key}"


def poll_bedrock_server(server: Server):
    """Polls a bedrock server for information"""

    # TODO: Add test for this

    ip = server.bedrock_ip_address

    if server.bedrock_port:
        ip = f"{ip}:{server.bedrock_port}"

    minecraft_server = BedrockServer.lookup(ip)

    try:
        status: BedrockStatusResponse = minecraft_server.status()
        server.is_online = True
        server.players = status.players.online
        server.max_players = status.players.max
    except Exception as e:
        server.is_online = False
        server.players = 0

    with _handle_db_errors():
        db.session.commit()


def poll_java_server(server: Server):
    """Polls a java server for information"""

    # TODO: Add test for this

    ip = server.java_ip_address

    if server.java_port:
        ip = f"{ip}:{server.java_port}"

    minecraft_server = JavaServer.lookup(ip)
    commited = False

    try:
        status: JavaStatusResponse = minecraft_server.status()

        server.is_online = True

        logger.info("is online")
        # TODO: Add MOTD
        # server.motd = status.description
        server.players = status.players.online
        server.max_players = status.players.max
        # server.version = status.version.name

        logger.info(f"has players {status.players.online}")
        logger.info(f"max players {status.players.max}")

        if status.icon:
            logger.info("has icon")
            server.icon_url = _upload_server_icon(status.icon)

    except Exception as e:
        server.is_online = False
        server.players = 0
        logger.info("is offline")
        logger.info("failed to get status")

    with _handle_db_errors():
        db.session.commit()
        commited = True

    # If we have commited, we don't need to check query
    if commited:
        return

    try:
        query: QueryResponse = server.query()

        server.is_online = True
        server.players = query.players.online
        server.max_players = query.players.max
        # TODO Add these fields
        # server.minecraft_version = query.software.version
        # server.plugins = query.software.plugins
        # server.map = query.map
        # server.motd = query.motd.clean
        # server.player_names = query.players.names

    except Exception as e:
        server.is_online = False
        server.players = 0

    with _handle_db_errors():
        db.session.commit()


def poll_servers():
    """Polls minecraft servers for information"""

    logger.info("Polling servers")

    # Get all servers
    servers = db.session.query(Server).all()

    for server in servers:
        # check what type of server we are dealing with

        if server.java_ip_address:
            poll_java_server(server)

        if server.bedrock_ip_address:
            poll_bedrock_server(server)

    db.end_session()
