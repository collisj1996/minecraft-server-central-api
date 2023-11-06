from contextlib import contextmanager
from uuid import UUID
import boto3

from sqlalchemy.orm import Session

from msc.models.minecraft_version import MinecraftVersion, VersionType
from msc.errors import NotFound, BadRequest, Unauthorized, InternalError


@contextmanager
def _handle_db_errors():
    """Handles database errors"""
    try:
        yield
    except Exception as e:
        # TODO: Raise a custom exception here
        raise e


def get_versions(
    db: Session,
):
    """Gets minecraft versions from database"""

    versions = (
        db.query(MinecraftVersion)
        .filter(
            MinecraftVersion.type == VersionType.RELEASE,
        )
        .order_by(
            MinecraftVersion.release_time.desc(),
        )
        .all()
    )

    return versions
