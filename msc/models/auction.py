from datetime import datetime
from uuid import uuid4, UUID

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    UniqueConstraint,
    CheckConstraint,
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
    bidding_starts_at = Column(DateTime, nullable=False)
    bidding_ends_at = Column(DateTime, nullable=False)
    payment_starts_at = Column(DateTime, nullable=False)
    payment_ends_at = Column(DateTime, nullable=False)
    sponsored_starts_at = Column(DateTime, nullable=False)
    sponsored_ends_at = Column(DateTime, nullable=False)
    sponsored_slots = Column(Integer, nullable=False)
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
    )

    def __init__(
        self,
        bidding_starts_at: datetime,
        bidding_ends_at: datetime,
        payment_starts_at: datetime,
        payment_ends_at: datetime,
        sponsored_starts_at: datetime,
        sponsored_ends_at: datetime,
        minimum_bid: int,
        sponsored_slots: int,
    ):
        self.bidding_starts_at = bidding_starts_at
        self.bidding_ends_at = bidding_ends_at
        self.payment_starts_at = payment_starts_at
        self.payment_ends_at = payment_ends_at
        self.sponsored_starts_at = sponsored_starts_at
        self.sponsored_ends_at = sponsored_ends_at
        self.minimum_bid = minimum_bid
        self.sponsored_slots = sponsored_slots

        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now
