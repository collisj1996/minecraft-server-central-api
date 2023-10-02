from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    Text,
    UniqueConstraint,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from msc import db


class Server(db.Base):
    """
    Represents a server listing
    """

    __tablename__ = "server"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    java_ip_address = Column(Text, nullable=True)
    java_port = Column(Integer, nullable=True)
    bedrock_ip_address = Column(Text, nullable=True)
    bedrock_port = Column(Text, nullable=True)
    players = Column(Integer, nullable=False)
    max_players = Column(Integer, nullable=False)
    is_online = Column(Boolean, nullable=False, default=False)
    country_code = Column(Text, nullable=False)
    minecraft_version = Column(Text, nullable=False)
    votifier_ip_address = Column(Text, nullable=True)
    votifier_port = Column(Integer, nullable=True)
    votifier_key = Column(Text, nullable=True)
    website = Column(Text, nullable=True)
    discord = Column(Text, nullable=True)
    video_url = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    banner_checksum = Column(Text, nullable=True)
    banner_filetype = Column(Text, nullable=True)
    icon_checksum = Column(Text, nullable=True)
    last_pinged_at = Column(DateTime, nullable=True)
    owner_name = Column(Text, nullable=True)
    web_store = Column(Text, nullable=True)
    flagged_for_deletion = Column(Boolean, nullable=False)
    flagged_for_deletion_at = Column(DateTime, nullable=True)
    uptime = Column(Float, nullable=False)

    gameplay = relationship("ServerGameplay", backref="server")

    __table_args__ = (
        UniqueConstraint(
            "id",
            name="unique_server_id",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
        ),
        # check constraint to ensure that at least one of java_ip_address or bedrock_ip_address is not null
        CheckConstraint(
            "java_ip_address IS NOT NULL OR bedrock_ip_address IS NOT NULL",
            name="check_ip_address",
        ),
    )

    def __init__(
        self,
        user_id: UUID,
        name: str,
        description: str,
        country_code: str,
        minecraft_version: str,
        java_ip_address: Optional[str] = None,
        bedrock_ip_address: Optional[str] = None,
        java_port: Optional[int] = None,
        bedrock_port: Optional[int] = None,
        votifier_ip_address: Optional[str] = None,
        votifier_port: Optional[int] = None,
        votifier_key: Optional[str] = None,
        website: Optional[str] = None,
        discord: Optional[str] = None,
        banner_checksum: Optional[str] = None,
        banner_filetype: Optional[str] = None,
        video_url: Optional[str] = None,
        owner_name: Optional[str] = None,
        web_store: Optional[str] = None,
    ):
        self.name = name
        self.user_id = user_id
        self.description = description
        self.java_ip_address = java_ip_address
        self.bedrock_ip_address = bedrock_ip_address
        self.java_port = java_port
        self.bedrock_port = bedrock_port
        self.country_code = country_code
        self.minecraft_version = minecraft_version
        self.votifier_ip_address = votifier_ip_address
        self.votifier_port = votifier_port
        self.votifier_key = votifier_key
        self.website = website
        self.discord = discord
        self.players = 0
        self.max_players = 0
        self.banner_checksum = banner_checksum
        self.banner_filetype = banner_filetype
        self.video_url = video_url
        self.owner_name = owner_name
        self.web_store = web_store
        self.flagged_for_deletion = False
        self.uptime = 100.0

        current_datetime = datetime.utcnow()
        self.created_at = current_datetime
        self.updated_at = current_datetime
