from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    UniqueConstraint,
    DateTime,
    Boolean,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID

from msc import db


class ServerHistoryOld(db.Base):
    """
    Represents a historical data point for a server listing older than a month,
    data points are aggregated by day
    """

    __tablename__ = "server_history_old"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    server_id = Column(UUID(as_uuid=True), nullable=False)
    is_online = Column(Boolean, nullable=False)
    players = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "id",
            name="unique_server_history_old_id",
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
    ):
        self.server_id = server_id
        self.created_at = datetime.utcnow()
