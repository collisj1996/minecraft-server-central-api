from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from msc import db


class Vote(db.Base):
    """
    Represents a vote
    """

    __tablename__ = "vote"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    server_id = Column(UUID(as_uuid=True), nullable=False)
    client_ip_address = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["server_id"],
            ["server.id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "id",
            name="unique_vote_id",
        ),
    )

    def __init__(
        self,
        server_id: UUID,
        client_ip_address: str,
    ):
        self.server_id = server_id
        self.client_ip_address = client_ip_address
        self.created_at = datetime.utcnow()
