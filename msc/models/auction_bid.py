from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from msc.database import Base


class AuctionBid(Base):
    """
    Represents an auction bid
    """

    __tablename__ = "auction_bid"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    auction_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    server_id = Column(UUID(as_uuid=True), nullable=False)
    server_name = Column(Text, nullable=False)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    payment_status = Column(Text, nullable=True)

    server = relationship("Server")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint(
            "id",
            name="auction_bid_unique_id",
        ),
        UniqueConstraint(
            "auction_id",
            "server_id",
            name="auction_bid_unique_auction_id_server_id",
        ),
        UniqueConstraint(
            "auction_id",
            "amount",
            name="auction_bid_unique_auction_id_amount",
        ),
        ForeignKeyConstraint(
            ["auction_id"],
            ["auction.id"],
            name="auction_bid_auction_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="auction_bid_user_id_fkey",
        ),
        ForeignKeyConstraint(
            ["server_id"],
            ["server.id"],
            name="auction_bid_server_id_fkey",
        ),
        CheckConstraint(
            "amount > 0",
            name="auction_bid_amount_greater_than_zero",
        ),
    )

    def __init__(
        self,
        auction_id: UUID,
        user_id: UUID,
        server_id: UUID,
        server_name: str,
        amount: int,
    ):
        self.auction_id = auction_id
        self.user_id = user_id
        self.server_id = server_id
        self.server_name = server_name
        self.amount = amount

        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now
