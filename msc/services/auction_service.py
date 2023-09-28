from contextlib import contextmanager
from datetime import datetime
from uuid import UUID
from dataclasses import dataclass

from msc.models import Auction, AuctionBid, Server, User
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from msc.errors import NotFound, BadRequest, Unauthorized
from msc.constants import MINIMUM_BID_DEFAULT, SPONSORED_SLOTS_DEFAULT


class InvalidBidAmount(BadRequest):
    """Raised when the bid amount is invalid"""


class InvalidBid(BadRequest):
    """Raised when the bid is invalid"""


@dataclass
class GetAuctionInfo:
    auction: Auction
    bids: list[AuctionBid]


@contextmanager
def _handle_db_errors():
    """Handles database errors"""
    try:
        yield
    except Exception as e:
        # TODO: Raise a custom exception here
        raise e


def create_auction(
    db: Session,
    bidding_starts_at: datetime,
    bidding_ends_at: datetime,
    payment_starts_at: datetime,
    payment_ends_at: datetime,
    sponsored_starts_at: datetime,
    sponsored_ends_at: datetime,
    minimum_bid: int = MINIMUM_BID_DEFAULT,
    sponsored_slots_default: int = SPONSORED_SLOTS_DEFAULT,
):
    """Adds an auction to the database"""

    auction = Auction(
        bidding_starts_at=bidding_starts_at,
        bidding_ends_at=bidding_ends_at,
        payment_starts_at=payment_starts_at,
        payment_ends_at=payment_ends_at,
        sponsored_starts_at=sponsored_starts_at,
        sponsored_ends_at=sponsored_ends_at,
        minimum_bid=minimum_bid,
        sponsored_slots=sponsored_slots_default,
    )

    with _handle_db_errors():
        db.add(auction)
        db.commit()

    return auction


def add_auction_bid(
    db: Session,
    auction_id: UUID,
    user_id: UUID,
    server_id: UUID,
    amount: int,
):
    """Adds an auction bid to the database"""

    server = db.query(Server).filter(Server.id == server_id).one_or_none()
    user = db.query(User).filter(User.id == user_id).one_or_none()
    auction = db.query(Auction).filter(Auction.id == auction_id).one_or_none()

    if server is None:
        raise NotFound("Server not found")

    if user is None:
        raise NotFound("User not found")

    if auction is None:
        raise NotFound("Auction not found")

    if amount <= auction.minimum_bid:
        raise InvalidBidAmount("Bid amount must be greater than the minimum bid")

    if server.user_id != user_id:
        raise Unauthorized("You are not authorized to bid on this server")

    if datetime.now() < auction.bidding_starts_at:
        raise InvalidBid("Bidding has not started yet")

    if datetime.now() > auction.bidding_ends_at:
        raise InvalidBid("Bidding has ended")

    user_max_bid = (
        db.query(AuctionBid)
        .filter(
            AuctionBid.auction_id == auction_id,
            AuctionBid.user_id == user_id,
            AuctionBid.server_id == server_id,
        )
        .order_by(
            AuctionBid.amount.desc(),
        )
        .first()
    )

    if user_max_bid is not None and amount <= user_max_bid.amount:
        raise InvalidBidAmount("Bid amount must be greater than your current max bid")

    auction_bid = AuctionBid(
        auction_id=auction_id,
        user_id=user_id,
        server_id=server_id,
        server_name=server.name,
        amount=amount,
    )

    with _handle_db_errors():
        db.add(auction_bid)
        db.commit()

    return auction_bid


def get_auction(db: Session, auction_id: UUID):
    """Gets an auction from the database and the associated bids"""

    auction = db.query(Auction).filter(Auction.id == auction_id).one_or_none()

    if auction is None:
        raise NotFound("Auction not found")

    subquery = (
        db.query(
            AuctionBid.server_id,
            func.max(AuctionBid.amount).label("max_bid"),
        )
        .filter(AuctionBid.auction_id == auction_id)
        .group_by(AuctionBid.server_id)
        .subquery()
    )

    # TODO: Add a test for this
    bids = (
        db.query(AuctionBid)
        .join(
            subquery,
            and_(
                AuctionBid.server_id == subquery.c.server_id,
                AuctionBid.amount == subquery.c.max_bid,
            ),
        )
        .filter(AuctionBid.auction_id == auction_id)
        .all()
    )

    return GetAuctionInfo(auction=auction, bids=bids)


def get_auctions(db: Session):
    """Gets all auctions from the database"""

    # TODO: implement this

    return []
