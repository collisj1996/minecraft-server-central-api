import base64
from contextlib import contextmanager
from typing import Optional

import boto3

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


def upload_banner(banner_base64: str):
    """Uploads a banner to S3 and returns the URL, raises an exception if the upload fails"""

    s3 = boto3.client("s3")

    # TODO: Add validation here to ensure the banner is a valid image

    try:
        print(1)
    except Exception as e:
        raise e

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

    if banner_base64:
        upload_banner(banner_base64)

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
    )

    db.session.add(server)

    with _handle_db_errors():
        db.session.commit()

    return server