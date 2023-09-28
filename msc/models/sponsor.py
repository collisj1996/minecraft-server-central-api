from datetime import datetime
from uuid import uuid4, UUID

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from msc import db


class Sponsor(db.Base):
    """
    Represents an sponsor
    """

    __tablename__ = "sponsor"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    server_id = Column(UUID(as_uuid=True), nullable=False)
    slot = Column(Integer, nullable=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="sponsor_user_id_fkey",
        ),
        ForeignKeyConstraint(
            ["server_id"],
            ["server.id"],
            name="sponsor_server_id_fkey",
        ),
        UniqueConstraint(
            "id",
            name="sponsor_unique_id",
        ),
        CheckConstraint(
            "ends_at > starts_at",
            name="sponsor_ends_at_after_starts_at",
        ),
    )

    def __init__(
        self,
        user_id: UUID,
        server_id: UUID,
        slot: int,
        starts_at: datetime,
        ends_at: datetime,
    ):
        self.user_id = user_id
        self.server_id = server_id
        self.slot = slot
        self.starts_at = starts_at
        self.ends_at = ends_at

        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now
