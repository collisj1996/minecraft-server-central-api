from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from msc.constants import MINIMUM_BID_DEFAULT, SPONSORED_SLOTS_DEFAULT
from msc.errors import BadRequest, NotFound, Unauthorized
from msc.models import Auction, AuctionBid, Server, User


class InvalidBidAmount(BadRequest):
    """Raised when the bid amount is invalid"""


class InvalidBid(BadRequest):
    """Raised when the bid is invalid"""


class OnlyOneCurrentAuctionBadRequest(BadRequest):
    """Raised when there is already a current auction"""


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
        if e.orig.diag.constraint_name == "idx_current_auction":
            raise OnlyOneCurrentAuctionBadRequest(
                "There can only be one current auction"
            )

        raise e


def create_auction(
    db: Session,
    sponsored_year: int,
    sponsored_month: int,
    minimum_bid: int = MINIMUM_BID_DEFAULT,
    sponsored_slots_default: int = SPONSORED_SLOTS_DEFAULT,
    is_current_auction: bool = False,
):
    """Adds an auction to the database"""

    auction = Auction(
        sponsored_year=sponsored_year,
        sponsored_month=sponsored_month,
        minimum_bid=minimum_bid,
        sponsored_slots=sponsored_slots_default,
        is_current_auction=is_current_auction,
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

    server = (
        db.query(Server)
        .filter(
            Server.id == server_id,
            Server.flagged_for_deletion == False,
        )
        .one_or_none()
    )
    user = db.query(User).filter(User.id == user_id).one_or_none()
    auction = db.query(Auction).filter(Auction.id == auction_id).one_or_none()

    # TODO: Add test for flagged_for_deletion
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

    if not auction.is_current_auction:
        raise InvalidBid("This auction is not the currently active auction")

    now = datetime.now()

    if now < auction.bidding_starts_at:
        raise InvalidBid("Bidding has not started yet")

    if now > auction.bidding_ends_at:
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


def get_current_auction(db: Session) -> GetAuctionInfo:
    """Gets the current auction from the database"""

    auction = (
        db.query(Auction)
        .filter(Auction.is_current_auction == True)
        .order_by(Auction.created_at.desc())
        .first()
    )

    if auction is None:
        raise NotFound("There is no current auction")

    auction_info = _get_auction(db=db, auction_id=auction.id)

    return auction_info


def _get_auction(db: Session, auction_id: UUID) -> GetAuctionInfo:
    """Gets an auction from the database"""

    auction = (
        db.query(Auction)
        .filter(
            Auction.id == auction_id,
        )
        .one_or_none()
    )

    if auction is None:
        raise NotFound("Auction not found")

    subquery = (
        db.query(
            AuctionBid.server_id,
            func.max(AuctionBid.amount).label("max_bid"),
        )
        # TODO: Add test for flagged_for_deletion
        .join(Server, Server.id == AuctionBid.server_id)
        .filter(
            AuctionBid.auction_id == auction_id,
            Server.flagged_for_deletion == False,
        )
        .group_by(AuctionBid.server_id)
        .subquery()
    )

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
        .order_by(subquery.c.max_bid.desc())
        .limit(auction.sponsored_slots)
        .all()
    )

    return GetAuctionInfo(auction=auction, bids=bids)


def get_auction(db: Session, auction_id: UUID) -> GetAuctionInfo:
    """Gets an auction from the database and the associated bids"""

    return _get_auction(db=db, auction_id=auction_id)


def get_auctions(
    db: Session,
    page: int = 1,
    per_page: int = 10,
    include_current_auction: bool = False,
) -> list[GetAuctionInfo]:
    """Gets all auctions from the database and the associated bids"""

    auctions = (
        db.query(Auction)
        .filter(
            or_(
                Auction.is_current_auction == False,
                Auction.is_current_auction == include_current_auction,
            )
        )
        .order_by(Auction.sponsored_ends_at.desc())
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

    auction_ids = [auction.id for auction in auctions]

    subquery = (
        db.query(
            AuctionBid.auction_id,
            AuctionBid.server_id,
            func.max(AuctionBid.amount).label("max_bid"),
        )
        .join(
            Server,
            Server.id == AuctionBid.server_id,
        )
        # TODO: Add test for flagged_for_deletion
        .filter(
            AuctionBid.auction_id.in_(auction_ids),
            Server.flagged_for_deletion == False,
        )
        .group_by(
            AuctionBid.auction_id,
            AuctionBid.server_id,
        )
        .subquery()
    )

    bids = (
        db.query(AuctionBid)
        .join(
            subquery,
            and_(
                AuctionBid.auction_id == subquery.c.auction_id,
                AuctionBid.amount == subquery.c.max_bid,
            ),
        )
        .filter(AuctionBid.auction_id.in_(auction_ids))
        .order_by(subquery.c.max_bid.desc())
        .all()
    )

    auction_bids = defaultdict(list)

    for bid in bids:
        auction_bids[bid.auction_id].append(bid)

    auction_infos = []

    for auction in auctions:
        auction_infos.append(
            GetAuctionInfo(
                auction=auction,
                bids=auction_bids[auction.id],
            )
        )

    return auction_infos


def unset_current_auction(db: Session) -> GetAuctionInfo:
    """Unsets the current auction"""

    current_auction = (
        db.query(Auction)
        .filter(Auction.is_current_auction == True)
        .order_by(Auction.created_at.desc())
        .first()
    )

    if current_auction is None:
        raise NotFound("There is no current auction")

    current_auction.is_current_auction = False

    with _handle_db_errors():
        db.commit()

    auction_info = _get_auction(db=db, auction_id=current_auction.id)

    return auction_info


def change_current_auction(
    db: Session,
    auction_id: UUID,
) -> GetAuctionInfo:
    """Changes the current auction"""

    auction = (
        db.query(Auction)
        .filter(
            Auction.id == auction_id,
        )
        .one_or_none()
    )

    if auction is None:
        raise NotFound("Auction not found")

    current_auction = (
        db.query(Auction)
        .filter(Auction.is_current_auction == True)
        .order_by(Auction.created_at.desc())
        .first()
    )

    if current_auction is not None:
        if current_auction.id == auction.id:
            raise BadRequest("This auction is already the current auction")

        current_auction.is_current_auction = False

        with _handle_db_errors():
            db.flush()

    auction.is_current_auction = True

    with _handle_db_errors():
        db.commit()

    auction_info = _get_auction(db=db, auction_id=auction.id)

    return auction_info
