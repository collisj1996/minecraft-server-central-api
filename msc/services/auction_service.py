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
from msc.services import server_service


class InvalidBidAmount(BadRequest):
    """Raised when the bid amount is invalid"""


class InvalidBid(BadRequest):
    """Raised when the bid is invalid"""


class OnlyOneCurrentAuctionBadRequest(BadRequest):
    """Raised when there is already a current auction"""


class ServerNotEligibleForAuctionBadRequest(BadRequest):
    """Raised when the server is not eligible for auction"""


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

    # TODO: Add test for is_eligible_for_auction
    if not server_service.is_eligible_for_auction(server=server):
        raise ServerNotEligibleForAuctionBadRequest(
            "This server is not eligible for sponsored auction"
        )

    now = datetime.now()

    if now < auction.bidding_starts_at:
        raise InvalidBid("Bidding has not started yet")

    if now > auction.bidding_ends_at:
        raise InvalidBid("Bidding has ended")

    server_bid = (
        db.query(AuctionBid)
        .filter(
            AuctionBid.auction_id == auction_id,
            AuctionBid.user_id == user_id,
            AuctionBid.server_id == server_id,
        )
        .one_or_none()
    )

    if server_bid is not None and amount <= server_bid.amount:
        raise InvalidBidAmount("Bid amount must be greater than your current bid")

    response = None

    if server_bid:
        server_bid.amount = amount
        server_bid.updated_at = now
        response = server_bid
    else:
        auction_bid = AuctionBid(
            auction_id=auction_id,
            user_id=user_id,
            server_id=server_id,
            server_name=server.name,
            amount=amount,
        )
        db.add(auction_bid)
        response = auction_bid

    with _handle_db_errors():
        db.commit()

    return response


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

    bids = (
        db.query(AuctionBid)
        .filter(AuctionBid.auction_id == auction_id)
        .order_by(AuctionBid.amount.desc())
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

    bids = (
        db.query(AuctionBid)
        .filter(AuctionBid.auction_id.in_(auction_ids))
        .order_by(AuctionBid.amount.desc())
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


def get_bid(db: Session, user_id: UUID, auction_id: UUID, server_id: UUID):
    """Gets a bid from the database"""

    user = db.query(User).filter(User.id == user_id).one_or_none()

    if user is None:
        raise NotFound("User not found")

    auction = db.query(Auction).filter(Auction.id == auction_id).one_or_none()

    if auction is None:
        raise NotFound("Auction not found")

    server = db.query(Server).filter(Server.id == server_id).one_or_none()

    if server is None:
        raise NotFound("Server not found")

    if server.user_id != user_id:
        raise NotFound("Bid not found")

    bid = (
        db.query(AuctionBid)
        .filter(
            AuctionBid.auction_id == auction_id,
            AuctionBid.user_id == user_id,
            AuctionBid.server_id == server_id,
        )
        .one_or_none()
    )

    if bid is None:
        raise NotFound("Bid not found")

    return bid
