import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Index, String

from msc.database import Base


class VersionType(str, enum.Enum):
    RELEASE = "Release"
    SNAPSHOT = "Snapshot"


class MinecraftVersion(Base):
    """
    Maintains all minecraft versions
    """

    __tablename__ = "minecraft_version"

    version = Column(String, primary_key=True, nullable=False)
    is_latest = Column(Boolean, nullable=False)
    type = Column(Enum(VersionType), nullable=False)
    release_time = Column(DateTime, nullable=False)

    __table_args__ = (
        Index(
            "idx_minecraft_version_is_latest_type",
            "is_latest",
            "type",
            unique=True,
            postgresql_where=is_latest.is_(True),
        ),
    )

    def __init__(
        self,
        version: str,
        is_latest: bool,
        type: VersionType,
        release_time: datetime,
    ):
        self.version = version
        self.is_latest = is_latest
        self.type = type
        self.release_time = release_time
