from msc.database import get_db
from msc.errors import InternalError
from sqlalchemy.orm import Session
from msc.models.minecraft_version import MinecraftVersion, VersionType

import requests
import logging

logger = logging.getLogger(__name__)


def _get_minecraft_versions() -> dict:
    VERSION_MANIFEST_URL = (
        "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    )

    try:
        response = requests.get(VERSION_MANIFEST_URL)

        if response.status_code == 200:
            json_data = response.json()
            return json_data
        else:
            raise InternalError(
                message="Status code not 200 when getting minecraft versions"
            )

    except Exception as e:
        logger.error("Unhandled error getting minecraft versions", e)
        raise InternalError(message="Unhandled error getting minecraft versions")


# def update_latest_minecraft_version():
#     db: Session = next(get_db())


def set_all_minecraft_versions():
    db: Session = next(get_db())

    versions = _get_minecraft_versions()

    latest = versions.get("latest")
    latest_release = latest.get("release")
    latest_snapshot = latest.get("snapshot")

    versions_ = versions.get("versions")

    if not versions_ or len(versions_) == 0:
        return

    # delete all versions
    db.query(MinecraftVersion).delete()

    for version in versions_:
        id_ = version.get("id")
        type = version.get("type")
        release_time = version.get("releaseTime")
        version_type = (
            VersionType.RELEASE if type == "release" else VersionType.SNAPSHOT
        )

        if id_ == latest_release:
            minecraft_version = MinecraftVersion(
                version=id_,
                is_latest=True,
                type=VersionType.RELEASE,
                release_time=release_time,
            )
        elif id_ == latest_snapshot:
            minecraft_version = MinecraftVersion(
                version=id_,
                is_latest=True,
                type=VersionType.SNAPSHOT,
                release_time=release_time,
            )
        else:
            minecraft_version = MinecraftVersion(
                version=id_,
                is_latest=False,
                type=version_type,
                release_time=release_time,
            )

        db.add(minecraft_version)
        db.commit()
