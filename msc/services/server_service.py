import base64
import re
from io import BytesIO
from contextlib import contextmanager
from typing import Optional
from uuid import UUID, uuid4

import boto3
from PIL import Image

from msc import db
from msc.models import Server


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

    servers = db.session.query(Server).all()

    # TODO: Add voting information
    # TODO: Add pagination here

    return servers


def upload_banner(banner_base64: str) -> str:
    """Uploads a banner to S3 and returns the URL, raises an exception if the upload fails"""
    # TODO: Add tests for this function

    # Remove metadata from base64 string
    base64_data = banner_base64.split("base64,")[1]

    # Decode the base64 image
    decoded_data = base64.b64decode(base64_data.encode() + b"==")

    # Create a BytesIO object from the decoded image
    image_data = BytesIO(decoded_data)


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

    s3 = boto3.client("s3")
    key = f"{uuid4()}.{img.format.lower()}"

    try:
        s3.put_object(
            Body=decoded_data,
            Bucket="cdn.minecraftservercentral.com",
            Key=f"{uuid4()}.{img.format.lower()}",
        )
    except Exception as e:
        raise e
    
    return f"https://cdn.minecraftservercentral.com/{key}"


def update_server():
    """Updates a server"""

    return "TODO"


def create_server(
    name: str,
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

    banner_url = upload_banner(banner_base64) if banner_base64 else None

    server = Server(
        name=name,
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
