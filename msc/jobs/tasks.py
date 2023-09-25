import logging
from contextlib import contextmanager
import boto3
from uuid import UUID
import base64
from socket import gaierror
from datetime import datetime

from mcstatus import BedrockServer, JavaServer
from mcstatus.status_response import JavaStatusResponse, BedrockStatusResponse
from mcstatus.querier import QueryResponse

from msc import db
from msc.models import Server
from msc.utils.file_utils import _get_checksum

logger = logging.getLogger(__name__)


@contextmanager
def _handle_db_errors():
    """Handles database errors"""
    try:
        yield
    except Exception as e:
        logger.error(f"Error adding server information: {e}")
        db.session.rollback()


def _upload_server_icon(
    icon_base64: str,
    server_id: UUID,
) -> str:
    """Uploads a server icon to S3 and returns the URL"""

    # Remove metadata from base64 string
    base64_data = icon_base64.split("base64,")[1]

    # Decode the base64 image
    decoded_data = base64.b64decode(base64_data.encode() + b"==")

    s3 = boto3.client("s3")
    key = f"icon/{server_id}.png"

    try:
        s3.put_object(
            Body=decoded_data,
            Bucket="cdn.minecraftservercentral.com",
            Key=key,
        )
    except Exception as e:
        logger.error(f"Error uploading server icon: {e}")


def poll_bedrock_server(server: Server):
    """Polls a bedrock server for information"""

    ip = server.bedrock_ip_address

    if server.bedrock_port:
        ip = f"{ip}:{server.bedrock_port}"

    minecraft_server = BedrockServer.lookup(ip)

    try:
        status: BedrockStatusResponse = minecraft_server.status()

        server.is_online = True
        server.players = status.players.online
        server.max_players = status.players.max
        server.last_pinged_at = datetime.utcnow()

    except TimeoutError as e:
        server.is_online = False
        server.players = 0
    except gaierror as e:
        server.is_online = False
        server.players = 0
    except Exception as e:
        server.is_online = False
        server.players = 0
        logger.error(f"Unhandled error polling bedrock server: {e}")

    with _handle_db_errors():
        db.session.commit()


def poll_java_server(server: Server):
    """Polls a java server for information"""

    ip = server.java_ip_address

    if server.java_port:
        ip = f"{ip}:{server.java_port}"

    minecraft_server = JavaServer.lookup(ip)
    commited = False

    try:
        status: JavaStatusResponse = minecraft_server.status()

        server.is_online = True
        server.players = status.players.online
        server.max_players = status.players.max
        server.last_pinged_at = datetime.utcnow()

        if status.icon:
            checksum = _get_checksum(status.icon)

            if checksum != server.icon_checksum:
                server.icon_checksum = checksum
                _upload_server_icon(
                    icon_base64=status.icon,
                    server_id=server.id,
                )
        else:
            server.icon_checksum = None

        with _handle_db_errors():
            db.session.commit()
            commited = True

    except TimeoutError as timeout_error:
        server.is_online = False
        server.players = 0
        # Dont commit here, we need to check query
    except gaierror as gai_error:
        server.is_online = False
        server.players = 0
        # Dont commit here, we need to check query
    except Exception as e:
        server.is_online = False
        server.players = 0
        logger.error(f"Unhandled error polling java server by status: {e}")
        # Dont commit here, we need to check query

    # If we have commited, we don't need to check query
    if commited:
        return

    try:
        query: QueryResponse = minecraft_server.query()

        server.is_online = True
        server.players = query.players.online
        server.max_players = query.players.max
        server.last_pinged_at = datetime.utcnow()

    except TimeoutError as timeout_error:
        server.is_online = False
        server.players = 0
    except Exception as e:
        server.is_online = False
        server.players = 0
        logger.error(f"Unhandled error polling java server by query: {e}")

    with _handle_db_errors():
        db.session.commit()


def poll_servers():
    """Polls minecraft servers for information"""

    logger.info("Polling servers")

    # Renew the session
    db.renew_session()

    # TODO: Do we want to make this async?
    servers = []

    # Get all servers
    with _handle_db_errors():
        servers = db.session.query(Server).all()

    for server in servers:
        # check what type of server we are dealing with

        if server.java_ip_address and server.bedrock_ip_address:
            # we only need to poll java server
            poll_java_server(server)
        else:
            if server.java_ip_address:
                poll_java_server(server)

            if server.bedrock_ip_address:
                poll_bedrock_server(server)

    db.end_session()
