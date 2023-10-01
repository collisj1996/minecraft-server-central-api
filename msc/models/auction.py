from datetime import datetime, timezone, timedelta
from uuid import uuid4, UUID
import calendar

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    UniqueConstraint,
    CheckConstraint,
    Boolean,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from msc import db


class Auction(db.Base):
    """
    Represents an auction
    """

    __tablename__ = "auction"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    is_current_auction = Column(Boolean, nullable=False)
    bidding_starts_at = Column(DateTime, nullable=False)
    bidding_ends_at = Column(DateTime, nullable=False)
    payment_starts_at = Column(DateTime, nullable=False)
    payment_ends_at = Column(DateTime, nullable=False)
    sponsored_starts_at = Column(DateTime, nullable=False)
    sponsored_ends_at = Column(DateTime, nullable=False)
    sponsored_slots = Column(Integer, nullable=False)
    sponsored_year = Column(Integer, nullable=False)
    sponsored_month = Column(Integer, nullable=False)
    minimum_bid = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    relationship = relationship("AuctionBid", backref="auction")

    __table_args__ = (
        CheckConstraint(
            "bidding_ends_at > bidding_starts_at",
            name="auction_bidding_ends_at_after_bidding_starts_at",
        ),
        CheckConstraint(
            "payment_ends_at > payment_starts_at",
            name="auction_payment_ends_at_after_payment_starts_at",
        ),
        CheckConstraint(
            "sponsored_ends_at > sponsored_starts_at",
            name="auction_sponsored_ends_at_after_sponsored_starts_at",
        ),
        CheckConstraint(
            "sponsored_starts_at > payment_ends_at",
            name="auction_sponsored_starts_at_after_payment_ends_at",
        ),
        CheckConstraint(
            "payment_starts_at > bidding_ends_at",
            name="auction_payment_starts_at_after_bidding_ends_at",
        ),
        CheckConstraint(
            "sponsored_slots > 0",
            name="auction_sponsored_slots_greater_than_zero",
        ),
        CheckConstraint(
            "minimum_bid > 0",
            name="auction_minimum_bid_greater_than_zero",
        ),
        UniqueConstraint(
            "id",
            name="auction_unique_id",
        ),
        UniqueConstraint(
            "sponsored_year",
            "sponsored_month",
            name="auction_unique_sponsored_year_and_month",
        ),
        CheckConstraint(
            "EXTRACT(YEAR FROM sponsored_starts_at) = sponsored_year AND EXTRACT(MONTH FROM sponsored_starts_at) = sponsored_month",
            name="auction_sponsored_starts_at_within_month",
        ),
        CheckConstraint(
            "EXTRACT(YEAR FROM sponsored_ends_at) = sponsored_year AND EXTRACT(MONTH FROM sponsored_ends_at) = sponsored_month",
            name="auction_sponsored_ends_at_within_month",
        ),
        Index(
            "idx_current_auction",
            "is_current_auction",
            unique=True,
            postgresql_where=is_current_auction.is_(True),
        ),
    )

    def __init__(
        self,
        is_current_auction: bool,
        sponsored_year: int,
        sponsored_month: int,
        minimum_bid: int,
        sponsored_slots: int,
    ):
        self.is_current_auction = is_current_auction
        self.minimum_bid = minimum_bid
        self.sponsored_slots = sponsored_slots

        self.sponsored_year = sponsored_year
        self.sponsored_month = sponsored_month

        # TODO: Add tests for this
        self.sponsored_starts_at = datetime(
            year=sponsored_year,
            month=sponsored_month,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc,
        )

        _, num_days = calendar.monthrange(sponsored_year, sponsored_month)

        self.sponsored_ends_at = datetime(
            year=sponsored_year,
            month=sponsored_month,
            day=num_days,
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
            tzinfo=timezone.utc,
        )

        self.bidding_starts_at = self.sponsored_starts_at - timedelta(days=14)
        self.bidding_ends_at = self.sponsored_starts_at - timedelta(days=3, hours=12)
        self.payment_starts_at = self.sponsored_starts_at - timedelta(
            days=3,
            hours=11,
            minutes=59,
        )
        self.payment_ends_at = self.sponsored_starts_at - timedelta(days=1)

        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now
