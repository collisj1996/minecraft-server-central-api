import base64
from contextlib import contextmanager
from datetime import datetime
from io import BytesIO
from typing import Optional
from uuid import uuid4, UUID

import boto3
from PIL import Image
from sqlalchemy import and_, desc, func

from msc import db
from msc.dto.custom_types import NOT_SET
from msc.models import Server, Vote


@contextmanager
def _handle_db_errors():
    """Handles database errors"""
    try:
        yield
    except Exception as e:
        db.session.rollback()
        # TODO: Raise a custom exception here
        raise e


def get_servers():
    """Returns all servers"""

    # Get the current month and year
    now = datetime.now()
    month = now.month
    year = now.year

    # Get servers and vote count
    servers_result = (
        db.session.query(
            Server,
            func.count(Vote.id).label("total_votes"),
            func.count(Vote.id)
            .filter(
                and_(
                    Vote.server_id == Server.id,
                    func.extract("month", Vote.created_at) == month,
                    func.extract("year", Vote.created_at) == year,
                )
            )
            .label("votes_this_month"),
        )
        .outerjoin(Vote, Server.id == Vote.server_id)
        .group_by(Server.id)
        .order_by(desc("votes_this_month"))
        .all()
    )

    # TODO: Add pagination here

    return servers_result


def get_server(server_id: UUID) -> Server:
    # Get the current month and year
    now = datetime.now()
    month = now.month
    year = now.year

    # get server with votes
    server_and_votes = (
        db.session.query(
            Server,
            func.count(Vote.id).label("total_votes"),
            func.count(Vote.id)
            .filter(
                and_(
                    Vote.server_id == Server.id,
                    func.extract("month", Vote.created_at) == month,
                    func.extract("year", Vote.created_at) == year,
                )
            )
            .label("votes_this_month"),
        )
        .outerjoin(Vote, Server.id == Vote.server_id)
        .filter(Server.id == server_id)
        .group_by(Server.id)
        .one_or_none()
    )

    if not server_and_votes:
        raise Exception("Server not found")

    return server_and_votes


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


def upload_banner(banner_base64: str) -> str:
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
    key = f"{uuid4()}.{img.format.lower()}"

    try:
        s3.put_object(
            Body=decoded_data,
            Bucket="cdn.minecraftservercentral.com",
            Key=key,
        )
    except Exception as e:
        raise e

    return f"https://cdn.minecraftservercentral.com/{key}"


def update_server(
    server_id: UUID,
    user_id: UUID,
    name: Optional[str] = NOT_SET,
    ip_address: Optional[str] = NOT_SET,
    country_code: Optional[str] = NOT_SET,
    minecraft_version: Optional[str] = NOT_SET,
    banner_base64: Optional[str] = NOT_SET,
    port: Optional[int] = NOT_SET,
    description: Optional[str] = NOT_SET,
    votifier_ip_address: Optional[str] = NOT_SET,
    votifier_port: Optional[int] = NOT_SET,
    votifier_key: Optional[str] = NOT_SET,
    website: Optional[str] = NOT_SET,
    discord: Optional[str] = NOT_SET,
) -> Server:
    """Updates a server"""

    server = (
        db.session.query(Server)
        .filter(
            Server.id == server_id,
        )
        .one_or_none()
    )

    if not server:
        raise Exception("Server not found")

    if server.user_id != user_id:
        raise Exception("You do not own this server")

    if name != NOT_SET:
        server.name = name

    if ip_address != NOT_SET:
        server.ip_address = ip_address

    if country_code != NOT_SET:
        server.country_code = country_code

    if minecraft_version != NOT_SET:
        server.minecraft_version = minecraft_version

    if banner_base64 != NOT_SET:
        server.banner_url = upload_banner(banner_base64)

    if port != NOT_SET:
        server.port = port

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

    with _handle_db_errors():
        db.session.commit()

    return server


def create_server(
    name: str,
    user_id: UUID,
    ip_address: str,
    country_code: str,
    minecraft_version: str,
    banner_base64: Optional[str] = None,
    port: Optional[int] = None,
    description: Optional[str] = None,
    votifier_ip_address: Optional[str] = None,
    votifier_port: Optional[int] = None,
    votifier_key: Optional[str] = None,
    website: Optional[str] = None,
    discord: Optional[str] = None,
):
    """Creates a server"""

    # TODO: Add testing for this validation
    user_servers = db.session.query(Server).filter(Server.user_id == user_id).all()

    if len(user_servers) > 0:
        raise Exception("User already has a server")

    banner_url = upload_banner(banner_base64) if banner_base64 else None

    server = Server(
        name=name,
        user_id=user_id,
        description=description,
        ip_address=ip_address,
        port=port,
        country_code=country_code,
        minecraft_version=minecraft_version,
        votifier_ip_address=votifier_ip_address,
        votifier_port=votifier_port,
        votifier_key=votifier_key,
        website=website,
        discord=discord,
        banner_url=banner_url,
    )

    db.session.add(server)

    with _handle_db_errors():
        db.session.commit()

    return server


def delete_server(
    user_id: UUID,
    server_id: UUID,
):
    """Deletes a server"""

    server = (
        db.session.query(Server)
        .filter(
            Server.id == server_id,
        )
        .one_or_none()
    )

    if not server:
        raise Exception("Server not found")

    if server.user_id != user_id:
        raise Exception("You do not own this server")

    with _handle_db_errors():
        db.session.delete(server)
        db.session.commit()

    return server_id
