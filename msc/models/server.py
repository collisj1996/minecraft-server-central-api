from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID

from msc import db


class Server(db.Base):
    """
    Represents a server listing
    """

    __tablename__ = "server"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    ip_address = Column(Text, nullable=False)
    port = Column(Integer, nullable=True)
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
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    banner_url = Column(Text, nullable=True)

    # TODO: Add server database constraints

    def __init__(
        self,
        name,
        description,
        ip_address,
        port,
        country_code,
        minecraft_version,
        votifier_ip_address,
        votifier_port,
        votifier_key,
        website,
        discord,
        banner_url,
    ):
        self.name = name
        self.description = description
        self.ip_address = ip_address
        self.port = port
        self.country_code = country_code
        self.minecraft_version = minecraft_version
        self.votifier_ip_address = votifier_ip_address
        self.votifier_port = votifier_port
        self.votifier_key = votifier_key
        self.website = website
        self.discord = discord
        self.players = 0
        self.max_players = 0
        self.banner_url = banner_url

        current_datetime = datetime.utcnow()
        self.created_at = current_datetime
        self.updated_at = current_datetime
