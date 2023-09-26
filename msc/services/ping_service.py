import logging
from contextlib import contextmanager
import boto3
from uuid import UUID
import base64
from socket import gaierror
from typing import Optional, List
from datetime import datetime
import asyncio

from mcstatus import BedrockServer, JavaServer
from mcstatus.status_response import JavaStatusResponse, BedrockStatusResponse
from mcstatus.querier import QueryResponse

from msc.constants import ASYNC_POLL_BATCH_SIZE

from msc.models import Server
from msc.utils.file_utils import _get_checksum
from msc.errors import BadRequest, NotFound, Unauthorized
from msc.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ServerUnreachable(BadRequest):
    """Represents a 400 Bad Request error."""


@contextmanager
def _handle_db_errors():
    """Handles database errors"""
    try:
        yield
    except Exception as e:
        logger.error(f"Error adding server information: {e}")
        pass


def _is_server_online(
    java_ip_address: Optional[str] = None,
    java_port: Optional[int] = None,
    bedrock_ip_address: Optional[str] = None,
    bedrock_port: Optional[int] = None,
):
    """Checks if a minecraft server is online"""

    if java_ip_address and bedrock_ip_address:
        # we only need to poll java server
        return _check_java_server_online(
            java_ip_address=java_ip_address,
            java_port=java_port,
        )
    else:
        if java_ip_address:
            return _check_java_server_online(
                java_ip_address=java_ip_address,
                java_port=java_port,
            )

        if bedrock_ip_address:
            return _check_bedrock_server_online(
                bedrock_ip_address=bedrock_ip_address,
                bedrock_port=bedrock_port,
            )


def check_server_online(
    java_ip_address: Optional[str] = None,
    java_port: Optional[int] = None,
    bedrock_ip_address: Optional[str] = None,
    bedrock_port: Optional[int] = None,
):
    """Wraps the is_server_online function and raises an error if the server is offline"""

    if not _is_server_online(
        java_ip_address=java_ip_address,
        java_port=java_port,
        bedrock_ip_address=bedrock_ip_address,
        bedrock_port=bedrock_port,
    ):
        raise ServerUnreachable("Server is offline")


def _check_java_server_online(
    java_ip_address: str,
    java_port: Optional[int] = None,
):
    """Checks if a java server is online"""

    ip = java_ip_address

    if java_port:
        ip = f"{ip}:{java_port}"

    minecraft_server = JavaServer.lookup(ip)

    try:
        status: JavaStatusResponse = minecraft_server.status()
        return True
    except TimeoutError as timeout_error:
        pass
    except gaierror as gai_error:
        pass
    except Exception as e:
        logger.error(f"Unhandled error polling java server by status: {e}")
        pass

    try:
        query: QueryResponse = minecraft_server.query()
        return True
    except TimeoutError as timeout_error:
        pass
    except Exception as e:
        logger.error(f"Unhandled error polling java server by query: {e}")
        pass

    return False


def _check_bedrock_server_online(
    bedrock_ip_address: str,
    bedrock_port: Optional[int] = None,
):
    """Checks if a bedrock server is online"""

    ip = bedrock_ip_address

    if bedrock_port:
        ip = f"{ip}:{bedrock_port}"

    minecraft_server = BedrockServer.lookup(ip)

    try:
        status: BedrockStatusResponse = minecraft_server.status()
        return True
    except TimeoutError as timeout_error:
        pass
    except gaierror as gai_error:
        pass
    except Exception as e:
        logger.error(f"Unhandled error polling bedrock server: {e}")
        pass

    return False


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


def poll_bedrock_server(
    db: Session,
    server: Server,
    commit: bool = True,
) -> bool:
    """Polls a bedrock server for information

    :param server: The server to poll
    :param commit: Whether to commit the changes to the database

    :returns: True if the server is online, False if the server is offline"""

    ip = server.bedrock_ip_address

    if server.bedrock_port:
        ip = f"{ip}:{server.bedrock_port}"

    minecraft_server = BedrockServer.lookup(ip)

    is_online = False

    try:
        status: BedrockStatusResponse = minecraft_server.status()

        is_online = True
        server.is_online = is_online
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

    if commit:
        with _handle_db_errors():
            db.commit()

    if not is_online:
        return False


def poll_java_server(
    db: Session,
    server: Server,
    commit: bool = False,
) -> bool:
    """Polls a java server for information

    :param db: The database session
    :param server: The server to poll
    :param commit: Whether to commit the changes to the database

    :returns: True if the server is online, False if the server is offline"""

    ip = server.java_ip_address

    if server.java_port:
        ip = f"{ip}:{server.java_port}"

    minecraft_server = JavaServer.lookup(ip)

    is_online = False

    try:
        status: JavaStatusResponse = minecraft_server.status()

        is_online = True
        server.is_online = is_online
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

        if commit:
            with _handle_db_errors():
                db.commit()

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

    # If server is online by status, we dont need to check query
    if is_online:
        return True

    try:
        query: QueryResponse = minecraft_server.query()

        is_online = True
        server.is_online = is_online
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

    if commit:
        with _handle_db_errors():
            db.commit()

    if not is_online:
        return False


async def poll_bedrock_server_async(
    db: Session,
    server: Server,
):
    """Polls a bedrock server for information asyncronously"""

    ip = server.bedrock_ip_address

    if server.bedrock_port:
        ip = f"{ip}:{server.bedrock_port}"

    minecraft_server = BedrockServer.lookup(ip)

    is_online = False

    try:
        status: BedrockStatusResponse = await minecraft_server.async_status()

        is_online = True
        server.is_online = is_online
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
        db.commit()

    if not is_online:
        return


async def poll_java_server_async(
    db: Session,
    server: Server,
):
    """Polls a java server for information asyncronously"""

    ip = server.java_ip_address

    if server.java_port:
        ip = f"{ip}:{server.java_port}"

    is_online = False

    try:
        status: JavaStatusResponse = await (
            await JavaServer.async_lookup(ip)
        ).async_status()

        is_online = True
        server.is_online = is_online
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
            db.commit()

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

    # If server is online by status, we dont need to check query
    if is_online:
        return True

    try:
        query: QueryResponse = await (await JavaServer.async_lookup(ip)).async_query()

        is_online = True
        server.is_online = is_online
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
        db.commit()

    if not is_online:
        return False


def poll_server_by_id(
    db: Session,
    server_id: UUID,
    user_id: UUID,
):
    """Polls a server by ID for information"""

    server = (
        db.query(Server)
        .filter(
            Server.id == server_id,
        )
        .one_or_none()
    )

    if not server:
        raise NotFound("Server not found")

    if server.user_id != user_id:
        raise Unauthorized("You are not authorized to access this server")

    poll_server(
        server=server,
        commit=True,
    )

    return "success"


def poll_server(
    db: Session,
    server: Server,
    commit: bool = True,
):
    """Polls a server for information"""

    is_online = False

    if server.java_ip_address and server.bedrock_ip_address:
        # we only need to poll java server
        is_online = poll_java_server(
            db=db,
            server=server,
            commit=commit,
        )
    else:
        if server.java_ip_address:
            is_online = poll_java_server(
                db=db,
                server=server,
                commit=commit,
            )

        if server.bedrock_ip_address:
            is_online = poll_bedrock_server(
                db=db,
                server=server,
                commit=commit,
            )

    if not is_online:
        raise ServerUnreachable("Server is offline")


async def poll_server_async(
    db: Session,
    server: Server,
):
    """Polls a server for information asyncronously"""

    try:
        if server.java_ip_address and server.bedrock_ip_address:
            # we only need to poll java server
            await poll_java_server_async(
                db=db,
                server=server,
            )
        else:
            if server.java_ip_address:
                await poll_java_server_async(
                    db=db,
                    server=server,
                )

            if server.bedrock_ip_address:
                await poll_bedrock_server_async(
                    db=db,
                    server=server,
                )
    except Exception as e:
        return


async def _poll_servers_aynsc_batch(db: Session, servers: List[Server]):
    """Batches the polling of servers asyncronously"""

    for i in range(0, len(servers), ASYNC_POLL_BATCH_SIZE):
        await asyncio.wait(
            {
                asyncio.create_task(
                    poll_server_async(
                        db=db,
                        server=process_server,
                    )
                )
                for process_server in servers[i : i + ASYNC_POLL_BATCH_SIZE]
            }
        )
        print(f"Processed {i} servers")


def poll_servers_async():
    """Polls minecraft servers for information"""

    # create a new db session for this job
    db: Session = next(get_db())

    logger.info("Polling servers")

    servers = []

    # Get all servers
    with _handle_db_errors():
        servers = db.query(Server).all()

    asyncio.run(
        _poll_servers_aynsc_batch(
            db=db,
            servers=servers,
        )
    )
