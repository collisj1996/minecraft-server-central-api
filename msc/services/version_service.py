from contextlib import contextmanager
from uuid import UUID
import boto3
import logging

from sqlalchemy.orm import Session

from msc.models.minecraft_version import MinecraftVersion, VersionType
from msc.errors import NotFound, BadRequest, Unauthorized, InternalError

logger = logging.getLogger(__name__)


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


def process_version_from_ping(db: Session, raw_version: str) -> str:
    """Processes the raw version from the ping endpoint"""

    # check if raw version matches
    mc_version = (
        db.query(MinecraftVersion)
        .filter(
            MinecraftVersion.version == raw_version,
        )
        .one_or_none()
    )

    if mc_version is not None:
        return raw_version

    processed_version = ""

    # non-proxy version filtering
    # normally "[xxx] [version]"
    processed_components = raw_version.rsplit(" ", 1)

    if len(processed_components) > 1:
        processed_version = processed_components[1]

    # check if processed version matches
    mc_version = (
        db.query(MinecraftVersion)
        .filter(
            MinecraftVersion.version == processed_version,
        )
        .one_or_none()
    )

    if mc_version is not None:
        return processed_version

    logging.info("Starting proxy filtering")
    logging.info(f"Raw version: {raw_version}")

    # proxy version filtering
    # normally "[xxx] [version_1[-,]version_2[-,]version_n]"

    # lets remove whitespace first
    processed_version = raw_version.replace(" ", "")

    logging.info(f"Processed version - no WS: {processed_version}")

    # lets replace any "-" or "," with "#"
    processed_version = processed_version.replace("-", "#")
    processed_version = processed_version.replace(",", "#")

    logging.info(f"Processed version #: {processed_version}")

    processed_components = processed_version.rsplit("#", 1)

    if len(processed_components) > 1:
        processed_version = processed_components[1]

    logging.info(f"Processed version: {processed_version}")

    # Example: "1.20.x"
    if "x" in processed_version:
        # "1.20.%"
        version_like = f"{processed_version.split('x')[0]}%"

        mc_version = (
            db.query(MinecraftVersion)
            .filter(
                MinecraftVersion.version.like(version_like),
            )
            .order_by(MinecraftVersion.release_time.desc())
            .limit(1)
            .one_or_none()
        )

        if mc_version is not None:
            return mc_version.version

    else:
        mc_version = (
            db.query(MinecraftVersion)
            .filter(
                MinecraftVersion.version == processed_version,
            )
            .one_or_none()
        )

        if mc_version is not None:
            return processed_version

    # no match - default to latest release version
    latest_version = (
        db.query(MinecraftVersion)
        .filter(
            MinecraftVersion.type == VersionType.RELEASE,
            MinecraftVersion.is_latest == True,
        )
        .one_or_none()
    )

    if latest_version is not None:
        return latest_version.version

    return None
