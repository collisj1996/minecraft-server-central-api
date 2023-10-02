from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    UniqueConstraint,
    CheckConstraint,
    DateTime,
    Boolean,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID

from msc import db


class VoteHistory(db.Base):
    """
    Represents a historical data point for a votes for a server listing older than 30 days
    """

    __tablename__ = "vote_history"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    server_id = Column(UUID(as_uuid=True), nullable=False)
    new_vote_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "id",
            name="unique_vote_history_id",
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
        new_vote_count: int,
    ):
        self.server_id = server_id
        self.new_vote_count = new_vote_count

        self.created_at = datetime.utcnow()
