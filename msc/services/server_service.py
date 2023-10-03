import base64
from contextlib import contextmanager
from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Optional
from uuid import UUID
from dataclasses import dataclass

import boto3
from PIL import Image
from sqlalchemy import and_, desc, func, cast, Integer, Float, case, extract
from sqlalchemy.orm import Session

from msc.dto.custom_types import NOT_SET
from msc.errors import BadRequest, NotFound
from msc.models import Server, ServerGameplay, Vote, ServerHistory, ServerHistoryOld
from msc.services import ping_service
from msc.utils.file_utils import _get_checksum


@contextmanager
def _handle_db_errors():
    """Handles database errors"""
    try:
        yield
    except Exception as e:
        # TODO: Raise a custom exception here
        raise e


@dataclass
class GetServerInfo:
    server: Server
    votes_this_month: int
    total_votes: int
    rank: int


@dataclass
class GetServersInfo:
    servers: List[GetServerInfo]
    total_servers: int


@dataclass
class ServerHistoryInfo:
    date: datetime
    rank: float
    players: float
    uptime: float
    new_votes: int
    votes_this_month: int
    total_votes: int


def get_servers(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    filter: Optional[str] = None,
):
    """Returns all servers"""

    # TODO: Add filtering

    # Get the current month and year
    now = datetime.now()
    month = now.month
    year = now.year

    subquery = (
        db.query(
            Vote.server_id,
            func.count(Vote.id).label("votes_this_month_sub"),
        )
        .filter(
            and_(
                func.extract("month", Vote.created_at) == month,
                func.extract("year", Vote.created_at) == year,
            )
        )
        .group_by(Vote.server_id)
        .subquery()
    )

    # Get servers and vote count
    servers_query = (
        db.query(
            Server,
            func.count(Vote.id).label("total_votes"),
            func.coalesce(subquery.c.votes_this_month_sub, 0).label("votes_this_month"),
            func.rank()
            .over(
                order_by=subquery.c.votes_this_month_sub.desc().nulls_last(),
                partition_by=None,
            )
            .label("rank"),
        )
        .outerjoin(Vote, Server.id == Vote.server_id)
        .outerjoin(subquery, Server.id == subquery.c.server_id)
        .filter(Server.flagged_for_deletion == False)
        .group_by(Server.id, subquery.c.votes_this_month_sub, Server.created_at)
        .order_by(
            desc("votes_this_month"),
            Server.created_at.desc(),
        )
    )

    # Add pagination
    servers_query = servers_query.limit(page_size).offset((page - 1) * page_size)

    servers_result = servers_query.all()

    # get total number of servers
    total_servers = (
        db.query(
            func.count(Server.id),
        )
        .filter(
            Server.flagged_for_deletion == False,
        )
        .scalar()
    )

    return GetServersInfo(
        servers=[
            GetServerInfo(
                server=s[0], votes_this_month=s[2], total_votes=s[1], rank=s[3]
            )
            for s in servers_result
        ],
        total_servers=total_servers,
    )


def get_server(
    db: Session,
    server_id: UUID,
) -> Server:
    # Get the current month and year
    now = datetime.now()
    month = now.month
    year = now.year

    subquery = (
        db.query(
            Vote.server_id,
            func.count(Vote.id).label("votes_this_month_sub"),
        )
        .filter(
            and_(
                func.extract("month", Vote.created_at) == month,
                func.extract("year", Vote.created_at) == year,
            )
        )
        .group_by(Vote.server_id)
        .subquery()
    )

    # get server with votes
    server_and_votes = (
        db.query(
            Server,
            func.count(Vote.id).label("total_votes"),
            func.coalesce(subquery.c.votes_this_month_sub, 0).label("votes_this_month"),
        )
        .outerjoin(Vote, Server.id == Vote.server_id)
        .outerjoin(subquery, Server.id == subquery.c.server_id)
        .filter(
            Server.id == server_id,
            Server.flagged_for_deletion == False,
        )
        .group_by(Server.id, subquery.c.votes_this_month_sub, Server.created_at)
        .one_or_none()
    )

    if not server_and_votes:
        raise NotFound("Server not found")

    rank = get_server_rank(db=db, server=server_and_votes[0])

    return GetServerInfo(
        server=server_and_votes[0],
        votes_this_month=server_and_votes[2],
        total_votes=server_and_votes[1],
        rank=rank,
    )


def get_my_servers(
    db: Session,
    user_id: UUID,
):
    """Returns all servers owned by a user with vote count and no pagination"""

    # Get the current month and year
    now = datetime.now()
    month = now.month
    year = now.year

    subquery = (
        db.query(
            Vote.server_id,
            func.count(Vote.id).label("votes_this_month_sub"),
        )
        .filter(
            and_(
                func.extract("month", Vote.created_at) == month,
                func.extract("year", Vote.created_at) == year,
            )
        )
        .group_by(Vote.server_id)
        .subquery()
    )

    # Get servers and vote count
    servers_query = (
        db.query(
            Server,
            func.count(Vote.id).label("total_votes"),
            func.coalesce(subquery.c.votes_this_month_sub, 0).label("votes_this_month"),
        )
        .outerjoin(
            Vote,
            Server.id == Vote.server_id,
        )
        .outerjoin(
            subquery,
            Server.id == subquery.c.server_id,
        )
        .filter(
            Server.user_id == user_id,
            Server.flagged_for_deletion == False,
        )
        .group_by(
            Server.id,
            subquery.c.votes_this_month_sub,
            Server.created_at,
        )
        .order_by(
            desc("votes_this_month"),
            Server.created_at.desc(),
        )
    )

    my_servers_result = servers_query.all()

    return [
        GetServerInfo(
            server=my_server[0],
            votes_this_month=my_server[2],
            total_votes=my_server[1],
            rank=get_server_rank(db=db, server=my_server[0]),
        )
        for my_server in my_servers_result
    ]


def _validate_banner(image_data: BytesIO) -> Image.Image:
    # Open the image using PIL
    with Image.open(image_data) as img:
        # Check if the image is 468 x 60 pixels
        if img.size != (468, 60):
            raise ValueError("Banner must be 468 x 60 pixels")

        # Check if the image format is valid
        if img.format not in ["GIF", "PNG", "JPEG", "JPG"]:
            raise ValueError(
                "Invalid image format. Only GIF, PNG, and JPEG are supported."
            )

    return img


def _upload_banner(
    banner_base64: str,
    server_id: UUID,
) -> str:
    """Uploads a banner to S3 and returns the URL, raises an exception if the upload fails"""

    # Remove metadata from base64 string
    base64_data = banner_base64.split("base64,")[1]

    # Decode the base64 image
    decoded_data = base64.b64decode(base64_data.encode() + b"==")

    # Create a BytesIO object from the decoded image
    image_data = BytesIO(decoded_data)

    # Validate the image and return the PIL image
    img = _validate_banner(image_data)

    s3 = boto3.client("s3")
    key = f"banner/{server_id}.{img.format.lower()}"

    try:
        s3.put_object(
            Body=decoded_data,
            Bucket="cdn.minecraftservercentral.com",
            Key=key,
        )
    except Exception as e:
        raise e

    return img.format.lower()


def update_server(
    db: Session,
    server_id: UUID,
    user_id: UUID,
    name: Optional[str] = NOT_SET,
    java_ip_address: Optional[str] = NOT_SET,
    bedrock_ip_address: Optional[str] = NOT_SET,
    java_port: Optional[int] = NOT_SET,
    bedrock_port: Optional[int] = NOT_SET,
    country_code: Optional[str] = NOT_SET,
    minecraft_version: Optional[str] = NOT_SET,
    banner_base64: Optional[str] = NOT_SET,
    description: Optional[str] = NOT_SET,
    votifier_ip_address: Optional[str] = NOT_SET,
    votifier_port: Optional[int] = NOT_SET,
    votifier_key: Optional[str] = NOT_SET,
    website: Optional[str] = NOT_SET,
    discord: Optional[str] = NOT_SET,
    gameplay: Optional[List[str]] = NOT_SET,
    video_url: Optional[str] = NOT_SET,
    web_store: Optional[str] = NOT_SET,
    owner_name: Optional[str] = NOT_SET,
) -> Server:
    """Updates a server"""

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
        raise BadRequest("You do not own this server")

    if name != NOT_SET:
        server.name = name

    if java_ip_address != NOT_SET:
        server.java_ip_address = java_ip_address
    if bedrock_ip_address != NOT_SET:
        server.bedrock_ip_address = bedrock_ip_address
    if java_port != NOT_SET:
        server.java_port = java_port
    if bedrock_port != NOT_SET:
        server.bedrock_port = bedrock_port
    if country_code != NOT_SET:
        server.country_code = country_code
    if minecraft_version != NOT_SET:
        server.minecraft_version = minecraft_version

    if banner_base64 != NOT_SET:
        if banner_base64 is None:
            server.banner_checksum = None
            server.banner_filetype = None
        else:
            banner_checksum = _get_checksum(banner_base64)
            if banner_checksum != server.banner_checksum:
                server.banner_checksum = banner_checksum
                server.banner_filetype = _upload_banner(
                    banner_base64=banner_base64,
                    server_id=server_id,
                )

    if description != NOT_SET:
        server.description = description
    if votifier_ip_address != NOT_SET:
        server.votifier_ip_address = votifier_ip_address
    if votifier_port != NOT_SET:
        server.votifier_port = votifier_port
    if votifier_key != NOT_SET:
        server.votifier_key = votifier_key
    if website != NOT_SET:
        server.website = website
    if discord != NOT_SET:
        server.discord = discord
    if video_url != NOT_SET:
        server.video_url = video_url
    if web_store != NOT_SET:
        server.web_store = web_store
    if owner_name != NOT_SET:
        server.owner_name = owner_name

    if gameplay != NOT_SET:
        # Delete all gameplay
        db.query(ServerGameplay).filter(
            ServerGameplay.server_id == server_id,
        ).delete()

        # Add new gameplay
        for gameplay_name in gameplay:
            server_gameplay = ServerGameplay(
                server_id=server_id,
                name=gameplay_name,
            )

            db.add(server_gameplay)

    # poll the server to check it is online and get extra data
    ping_service.poll_server(
        db=db,
        server=server,
        commit=False,
    )

    server.updated_at = datetime.now()

    with _handle_db_errors():
        db.commit()

    return server


def create_server(
    db: Session,
    name: str,
    user_id: UUID,
    country_code: str,
    minecraft_version: str,
    gameplay: List[str],
    java_ip_address: Optional[str] = None,
    bedrock_ip_address: Optional[str] = None,
    java_port: Optional[int] = None,
    bedrock_port: Optional[int] = None,
    banner_base64: Optional[str] = None,
    description: Optional[str] = None,
    votifier_ip_address: Optional[str] = None,
    votifier_port: Optional[int] = None,
    votifier_key: Optional[str] = None,
    website: Optional[str] = None,
    discord: Optional[str] = None,
    video_url: Optional[str] = None,
    web_store: Optional[str] = None,
    owner_name: Optional[str] = None,
) -> Server:
    """Creates a server"""

    user_servers = (
        db.query(Server)
        .filter(
            Server.user_id == user_id,
        )
        .all()
    )

    # TODO: Add this back in after testing
    # if len(user_servers) > 9:
    #     raise BadRequest(
    #         "You cannot create more than 10 servers",
    #         user_id=user_id,
    #     )

    server = Server(
        name=name,
        user_id=user_id,
        description=description,
        java_ip_address=java_ip_address,
        bedrock_ip_address=bedrock_ip_address,
        java_port=java_port,
        bedrock_port=bedrock_port,
        country_code=country_code,
        minecraft_version=minecraft_version,
        votifier_ip_address=votifier_ip_address,
        votifier_port=votifier_port,
        votifier_key=votifier_key,
        website=website,
        discord=discord,
        video_url=video_url,
        web_store=web_store,
        owner_name=owner_name,
    )

    db.add(server)

    with _handle_db_errors():
        db.flush()

    # poll the server to check it is online and get extra data
    ping_service.poll_server(
        db=db,
        server=server,
        commit=False,
    )

    if banner_base64:
        banner_checksum = _get_checksum(banner_base64)

        file_type = _upload_banner(
            banner_base64=banner_base64,
            server_id=server.id,
        )

        server.banner_filetype = file_type
        server.banner_checksum = banner_checksum

    for gameplay_name in gameplay:
        server_gameplay = ServerGameplay(
            server_id=server.id,
            name=gameplay_name,
        )

        db.add(server_gameplay)

    with _handle_db_errors():
        db.commit()

    return server


def delete_server(
    db: Session,
    user_id: UUID,
    server_id: UUID,
) -> UUID:
    """Deletes a server"""

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
        raise BadRequest("You do not own this server")

    server.flagged_for_deletion = True
    server.flagged_for_deletion_at = datetime.now()

    with _handle_db_errors():
        db.commit()

    return server_id


def get_server_history(
    db: Session,
    server_id: UUID,
    time_interval: str = "day",
) -> List[ServerHistory]:
    """Returns a server's historical data"""

    # TODO: Test this
    if time_interval not in ["day", "hour"]:
        raise BadRequest("Invalid time interval")

    server = (
        db.query(Server)
        .filter(
            Server.id == server_id,
            Server.flagged_for_deletion == False,
        )
        .one_or_none()
    )

    if not server:
        raise NotFound("Server not found")

    now = datetime.now()
    from_date = now - timedelta(days=30)
    to_date = now

    # TODO: Add rigourous testing for this
    server_history = (
        db.query(
            func.DATE_TRUNC(time_interval, ServerHistory.created_at).label("date"),
            cast(func.avg(ServerHistory.rank), Integer).label("rank"),
            cast(func.avg(ServerHistory.players), Integer).label("players"),
            cast(func.avg(ServerHistory.uptime), Float).label("uptime"),
            cast(func.sum(ServerHistory.new_votes), Integer).label("new_votes"),
            cast(func.max(ServerHistory.votes_this_month), Integer).label(
                "votes_this_month"
            ),
            cast(func.max(ServerHistory.total_votes), Integer).label("total_votes"),
        )
        .filter(
            ServerHistory.server_id == server_id,
            ServerHistory.created_at >= from_date,
            ServerHistory.created_at <= to_date,
        )
        .group_by("date")
        .order_by("date")
        .all()
    )

    server_history_infos = [
        ServerHistoryInfo(
            date=s[0],
            rank=s[1],
            players=s[2],
            uptime=s[3],
            new_votes=s[4],
            votes_this_month=s[5],
            total_votes=s[6],
        )
        for s in server_history
    ]

    return server_history_infos


def get_server_rank(
    db: Session,
    server: Server,
) -> int:
    """Gets a server's computed rank

    Mainly for internal use"""

    # Get the current month and year
    now = datetime.now()
    month = now.month
    year = now.year

    vote_subquery = (
        db.query(
            Vote.server_id,
            func.count(Vote.id).label("votes_this_month_sub"),
        )
        .filter(
            and_(
                func.extract("month", Vote.created_at) == month,
                func.extract("year", Vote.created_at) == year,
            )
        )
        .group_by(Vote.server_id)
        .subquery()
    )

    server_rank_subquery = (
        db.query(
            Server.id,
            func.rank()
            .over(
                order_by=vote_subquery.c.votes_this_month_sub.desc().nulls_last(),
                partition_by=None,
            )
            .label("rank"),
        )
        .outerjoin(
            vote_subquery,
            Server.id == vote_subquery.c.server_id,
        )
        .filter(
            Server.flagged_for_deletion == False,
        )
        .group_by(
            Server.id,
            vote_subquery.c.votes_this_month_sub,
            Server.created_at,
        )
        .subquery()
    )

    rank = (
        db.query(server_rank_subquery.c.rank)
        .filter(
            server_rank_subquery.c.id == server.id,
        )
        .scalar()
    )

    return rank
