import calendar
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from msc.database import Base


class Sponsor(Base):
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
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
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
        UniqueConstraint(
            "slot",
            "year",
            "month",
            name="sponsor_unique_slot_year_month",
        ),
        CheckConstraint(
            "ends_at > starts_at",
            name="sponsor_ends_at_after_starts_at",
        ),
        # TODO: Add test for this
        CheckConstraint(
            "slot > 0",
            name="sponsor_slot_greater_than_zero",
        ),
        # TODO: Add test for this
        CheckConstraint(
            "slot <= 10",
            name="sponsor_slot_less_than_or_equal_to_ten",
        ),
    )

    def __init__(
        self,
        user_id: UUID,
        server_id: UUID,
        slot: int,
        year: int,
        month: int,
    ):
        self.user_id = user_id
        self.server_id = server_id
        self.slot = slot
        self.year = year
        self.month = month

        self.starts_at = datetime(
            year=year,
            month=month,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc,
        )

        _, num_days = calendar.monthrange(year, month)

        self.ends_at = datetime(
            year=year,
            month=month,
            day=num_days,
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
            tzinfo=timezone.utc,
        )

        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now
