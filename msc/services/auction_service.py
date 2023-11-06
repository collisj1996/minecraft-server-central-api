from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from msc.constants import MINIMUM_BID_DEFAULT, SPONSORED_SLOTS_DEFAULT, BidPaymentStatus
from msc.database import get_db
from msc.errors import BadRequest, NotFound, Unauthorized
from msc.jobs.jobs import persisted_scheduler
from msc.models import Auction, AuctionBid, Server, Sponsor, User
from msc.services import email_service, server_service


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

        if e.orig.diag.constraint_name == "auction_bid_unique_auction_id_amount":
            raise InvalidBidAmount("Bid amount must be unique")

        raise e


def create_current_auction(
    db: Session,
    minimum_bid: int = MINIMUM_BID_DEFAULT,
    sponsored_slots: int = SPONSORED_SLOTS_DEFAULT,
) -> Auction:
    """Creates a new auction and makes it the new current auction, and sets up tasks for the auctions

    must be called inside the month that the auction is for"""

    # get the current auction
    auction = (
        db.query(Auction)
        .filter(Auction.is_current_auction == True)
        .order_by(Auction.created_at.desc())
        .first()
    )

    if auction is not None:
        auction.is_current_auction = False

        with _handle_db_errors():
            db.flush()

    now = datetime.utcnow()

    # add a month as we are sponsoring the next month
    next_month = now + relativedelta(months=+1)

    month = next_month.month
    year = next_month.year

    auction = Auction(
        sponsored_year=year,
        sponsored_month=month,
        minimum_bid=minimum_bid,
        sponsored_slots=sponsored_slots,
        is_current_auction=True,
    )

    with _handle_db_errors():
        db.add(auction)
        db.commit()

    # add a job to start the payment phase
    persisted_scheduler.add_job(
        start_payment_phase_task,
        "date",
        run_date=auction.payment_starts_at,
        timezone=timezone.utc,
    )

    # add a job to populate the sponsored servers
    persisted_scheduler.add_job(
        populate_sponsored_servers_task,
        "date",
        run_date=auction.sponsored_starts_at - timedelta(hours=12),
        timezone=timezone.utc,
    )

    return auction


def create_auction(
    db: Session,
    sponsored_year: int,
    sponsored_month: int,
    minimum_bid: int = MINIMUM_BID_DEFAULT,
    sponsored_slots: int = SPONSORED_SLOTS_DEFAULT,
    is_current_auction: bool = False,
) -> Auction:
    """Adds an auction to the database"""

    auction = Auction(
        sponsored_year=sponsored_year,
        sponsored_month=sponsored_month,
        minimum_bid=minimum_bid,
        sponsored_slots=sponsored_slots,
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

    now = datetime.utcnow()

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

    auction_info = _get_auction(
        db=db,
        auction_id=auction.id,
    )

    return auction_info


def _get_auction(
    db: Session,
    auction_id: UUID,
) -> GetAuctionInfo:
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

    now = datetime.utcnow()
    limit = (
        auction.sponsored_slots + 5
        if now >= auction.payment_starts_at
        else auction.sponsored_slots
    )

    bids = (
        db.query(AuctionBid)
        .filter(AuctionBid.auction_id == auction_id)
        .order_by(AuctionBid.amount.desc())
        .limit(limit)
        .all()
    )

    return GetAuctionInfo(auction=auction, bids=bids)


def get_auction(db: Session, auction_id: UUID) -> GetAuctionInfo:
    """Gets an auction from the database and the associated bids"""

    return _get_auction(db=db, auction_id=auction_id)


def get_historical_auctions(
    db: Session,
    page: int = 1,
    per_page: int = 10,
) -> list[GetAuctionInfo]:
    """Gets all auctions from the database and the associated bids"""

    auctions = (
        db.query(Auction)
        .filter(
            Auction.is_current_auction == False,
        )
        .order_by(Auction.sponsored_ends_at.desc())
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

    auction_ids = [auction.id for auction in auctions]

    bids = (
        db.query(AuctionBid)
        .filter(
            AuctionBid.auction_id.in_(auction_ids),
            AuctionBid.payment_status == BidPaymentStatus.PAID,
        )
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


def start_payment_phase_task() -> None:
    """Wraps the start_payment_phase function to be used as a task"""

    db: Session = next(get_db())

    start_payment_phase(db=db)

    db.close()


def start_payment_phase(db: Session) -> None:
    """Starts the payment phase, which sets bid_status for the top 15 auction bids"""

    current_auction = get_current_auction(db=db)

    # get the top sponsored_slots + 5 bids
    bids = (
        db.query(AuctionBid)
        .filter(AuctionBid.auction_id == current_auction.auction.id)
        .order_by(AuctionBid.amount.desc())
        .limit(current_auction.auction.sponsored_slots + 5)
        .all()
    )

    top_sponsored_slots_bids = bids[: current_auction.auction.sponsored_slots]
    next_five_bids = bids[current_auction.auction.sponsored_slots :]

    # set payment status to Awaiting Response for top sponsored_slots bids
    for bid in top_sponsored_slots_bids:
        bid.payment_status = BidPaymentStatus.AWAITING_RESPONSE

    # set payment status to Standby for the next 5 bids
    for bid in next_five_bids:
        bid.payment_status = BidPaymentStatus.STANDBY

    # send emails to top sponsored slots bids
    for index, bid in enumerate(top_sponsored_slots_bids):
        email_service.send_email(
            subject="Auction Winner!",
            recipient=bid.user.email,
            template="awaitingconfirmation",
            params={
                "recipient_name": bid.user.username,
                "server_name": bid.server.name,
                "sponsor_slot": index + 1,
                "bid_amount": bid.amount,
            },
        )

    with _handle_db_errors():
        db.commit()


def set_bid_payment_status(
    db: Session,
    bid_id: UUID,
    payment_status: BidPaymentStatus,
) -> AuctionBid:
    """Sets the bid payment status"""

    bid = db.query(AuctionBid).filter(AuctionBid.id == bid_id).one_or_none()

    if bid is None:
        raise NotFound("Bid not found")

    bid.payment_status = payment_status

    with _handle_db_errors():
        db.commit()

    return bid


def populate_sponsored_servers_task() -> None:
    """Wraps the populate_sponsored_servers function to be used as a task"""

    db: Session = next(get_db())

    populate_sponsored_servers(db=db)

    db.close()


def populate_sponsored_servers(db: Session):
    """Populates the the sponsor table with the Paid winners of the current auction,
    in time for them to be show during their sponsor period"""

    current_auction = get_current_auction(db=db)

    # get the top bids that have been paid
    bids = (
        db.query(AuctionBid)
        .filter(
            AuctionBid.auction_id == current_auction.auction.id,
            AuctionBid.payment_status == BidPaymentStatus.PAID,
        )
        .order_by(AuctionBid.amount.desc())
        .all()
    )

    now = datetime.utcnow()

    # add a month as we are sponsoring the next month
    next_month = now + relativedelta(months=+1)

    month = next_month.month
    year = next_month.year

    for index, bid in enumerate(bids):
        sponsor = Sponsor(
            user_id=bid.user_id,
            server_id=bid.server_id,
            slot=index + 1,
            year=year,
            month=month,
        )

        db.add(sponsor)

    with _handle_db_errors():
        db.commit()
