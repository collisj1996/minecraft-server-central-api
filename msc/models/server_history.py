from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from msc.database import Base


class ServerHistory(Base):
    """
    Represents a historical data point for a server listing for the past month
    """

    __tablename__ = "server_history"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    server_id = Column(UUID(as_uuid=True), nullable=False)
    is_online = Column(Boolean, nullable=False)
    uptime = Column(Integer, nullable=False)
    players = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=False)
    new_votes = Column(Integer, nullable=False)
    votes_this_month = Column(Integer, nullable=False)
    total_votes = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "id",
            name="unique_server_history_id",
        ),
        ForeignKeyConstraint(
            ["server_id"],
            ["server.id"],
            ondelete="CASCADE",
        ),
    )

    def __init__(
        self,
        server_id: UUID,
        is_online: bool,
        players: int,
        rank: int,
        uptime: int,
        new_votes: int,
        votes_this_month: int,
        total_votes: int,
    ):
        self.server_id = server_id
        self.is_online = is_online
        self.players = players
        self.rank = rank
        self.uptime = uptime
        self.new_votes = new_votes
        self.votes_this_month = votes_this_month
        self.total_votes = total_votes

        self.created_at = datetime.utcnow()
