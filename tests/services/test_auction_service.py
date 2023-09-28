from datetime import datetime
import pytest
from uuid import uuid4

from msc.models import Server, User, Auction, AuctionBid
from msc.services import auction_service
from msc.constants import MINIMUM_BID_DEFAULT, SPONSORED_SLOTS_DEFAULT
from msc.errors import NotFound, Unauthorized

import freezegun


def test_create_auction(
    session,
):
    """Tests creating an auction"""

    # using freezegun set the time to 1st of Jan 2021
    with freezegun.freeze_time(datetime(2021, 1, 1)):
        auction = auction_service.create_auction(
            db=session,
            bidding_starts_at=datetime(2021, 1, 18),
            bidding_ends_at=datetime(2021, 1, 28),
            payment_starts_at=datetime(2021, 1, 29),
            payment_ends_at=datetime(2021, 1, 30),
            sponsored_starts_at=datetime(2021, 2, 1),
            sponsored_ends_at=datetime(2021, 2, 28),
        )

    assert auction
    assert auction.bidding_starts_at == datetime(2021, 1, 18)
    assert auction.bidding_ends_at == datetime(2021, 1, 28)
    assert auction.payment_starts_at == datetime(2021, 1, 29)
    assert auction.payment_ends_at == datetime(2021, 1, 30)
    assert auction.sponsored_starts_at == datetime(2021, 2, 1)
    assert auction.sponsored_ends_at == datetime(2021, 2, 28)
    assert auction.minimum_bid == MINIMUM_BID_DEFAULT
    assert auction.sponsored_slots == SPONSORED_SLOTS_DEFAULT

    # assert Auction was added to the database
    assert session.query(Auction).filter(Auction.id == auction.id).one_or_none()


def test_bid_on_auction(
    session,
    user_jack: User,
    server_colcraft: Server,
    auction_inside_bidding_period: Auction,
):
    """Test that a user can bid on an auction for a server"""

    bid = auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=user_jack.id,
        server_id=server_colcraft.id,
        amount=100,
    )

    assert bid
    assert bid.auction_id == auction_inside_bidding_period.id
    assert bid.user_id == user_jack.id
    assert bid.server_id == server_colcraft.id
    assert bid.amount == 100

    # assert AuctionBid was added to the database
    assert (
        session.query(AuctionBid)
        .filter(AuctionBid.auction_id == auction_inside_bidding_period.id)
        .filter(AuctionBid.user_id == user_jack.id)
        .filter(AuctionBid.server_id == server_colcraft.id)
        .one_or_none()
    )


def test_bid_on_auction_with_invalid_auction_id(
    session,
    user_jack: User,
    server_colcraft: Server,
):
    """Test that a user cannot bid on an auction with an invalid auction id"""

    with pytest.raises(NotFound) as e:
        auction_service.add_auction_bid(
            db=session,
            auction_id=uuid4(),
            user_id=user_jack.id,
            server_id=server_colcraft.id,
            amount=100,
        )

    assert e.value.message == "Auction not found"


def test_bid_on_auction_with_invalid_user_id(
    session,
    server_colcraft: Server,
    auction_inside_bidding_period: Auction,
):
    """Test that a user cannot bid on an auction with an invalid user id"""

    with pytest.raises(NotFound) as e:
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_inside_bidding_period.id,
            user_id=uuid4(),
            server_id=server_colcraft.id,
            amount=100,
        )

    assert e.value.message == "User not found"


def test_bid_on_auction_with_invalid_server_id(
    session,
    user_jack: User,
    auction_inside_bidding_period: Auction,
):
    """Test that a user cannot bid on an auction with an invalid server id"""

    with pytest.raises(NotFound) as e:
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_inside_bidding_period.id,
            user_id=user_jack.id,
            server_id=uuid4(),
            amount=100,
        )

    assert e.value.message == "Server not found"


def test_bid_on_auction_with_amount_less_then_minimum(
    session,
    user_jack: User,
    server_colcraft: Server,
    auction_inside_bidding_period: Auction,
):
    """Test that a user cannot bid on an auction with an amount less then the minimum"""

    with pytest.raises(auction_service.InvalidBidAmount) as e:
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_inside_bidding_period.id,
            user_id=user_jack.id,
            server_id=server_colcraft.id,
            amount=0,
        )

    assert e.value.message == "Bid amount must be greater than the minimum bid"


def test_bid_on_auction_for_server_you_dont_own(
    session,
    user_alan: User,
    user_jack: User,
    server_colcraft: Server,
    auction_inside_bidding_period: Auction,
):
    """Test that a user cannot bid on an auction for a server they don't own"""

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=user_jack.id,
        server_id=server_colcraft.id,
        amount=100,
    )

    with pytest.raises(Unauthorized) as e:
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_inside_bidding_period.id,
            user_id=user_alan.id,
            server_id=server_colcraft.id,
            amount=100,
        )

    assert e.value.message == "You are not authorized to bid on this server"


def test_bid_on_auction_with_amount_less_then_max_bid(
    session,
    user_jack: User,
    server_colcraft: Server,
    auction_inside_bidding_period: Auction,
):
    """Test that a user cannot bid on an auction with an amount less then the previous bid"""

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=user_jack.id,
        server_id=server_colcraft.id,
        amount=100,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=user_jack.id,
        server_id=server_colcraft.id,
        amount=200,
    )

    with pytest.raises(auction_service.InvalidBidAmount) as e:
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_inside_bidding_period.id,
            user_id=user_jack.id,
            server_id=server_colcraft.id,
            amount=50,
        )

    assert e.value.message == "Bid amount must be greater than your current max bid"


def test_add_bid_before_bidding_period(
    session,
    user_jack: User,
    server_colcraft: Server,
    auction_before_bidding_period: Auction,
):
    """Test that a user cannot bid on an auction before the bidding period starts"""

    with pytest.raises(auction_service.InvalidBid) as e:
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_before_bidding_period.id,
            user_id=user_jack.id,
            server_id=server_colcraft.id,
            amount=100,
        )

    assert e.value.message == "Bidding has not started yet"


def test_add_bid_after_bidding_period(
    session,
    user_jack: User,
    server_colcraft: Server,
    auction_after_bidding_period: Auction,
):
    """Test that a user cannot bid on an auction after the bidding period ends"""

    with pytest.raises(auction_service.InvalidBid) as e:
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_after_bidding_period.id,
            user_id=user_jack.id,
            server_id=server_colcraft.id,
            amount=100,
        )

    assert e.value.message == "Bidding has ended"


def test_add_multiple_bids(
    session,
    user_jack: User,
    server_colcraft: Server,
    auction_inside_bidding_period: Auction,
):
    """Test that a user can add multiple bids"""

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=user_jack.id,
        server_id=server_colcraft.id,
        amount=100,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=user_jack.id,
        server_id=server_colcraft.id,
        amount=200,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=user_jack.id,
        server_id=server_colcraft.id,
        amount=300,
    )

    # assert AuctionBid was added to the database
    assert (
        session.query(AuctionBid)
        .filter(AuctionBid.auction_id == auction_inside_bidding_period.id)
        .filter(AuctionBid.user_id == user_jack.id)
        .filter(AuctionBid.server_id == server_colcraft.id)
        .count()
        == 3
    )


def test_user_can_bid_for_multiple_servers(
    session,
    user_jack: User,
    server_colcraft: Server,
    server_colcraft_2: Server,
    auction_inside_bidding_period: Auction,
):
    """Test that a user can bid for multiple servers"""

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=user_jack.id,
        server_id=server_colcraft.id,
        amount=100,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=user_jack.id,
        server_id=server_colcraft_2.id,
        amount=50,
    )

    # assert AuctionBid was added to the database
    assert (
        session.query(AuctionBid)
        .filter(AuctionBid.auction_id == auction_inside_bidding_period.id)
        .filter(AuctionBid.user_id == user_jack.id)
        .count()
        == 2
    )


def test_get_auction(
    session,
    auction: Auction,
):
    """Test getting an auction"""

    auction_result = auction_service.get_auction(
        db=session,
        auction_id=auction.id,
    )

    assert auction_result
    assert auction_result.id == auction.id
    assert auction_result.bidding_starts_at == auction.bidding_starts_at
    assert auction_result.bidding_ends_at == auction.bidding_ends_at
    assert auction_result.payment_starts_at == auction.payment_starts_at
    assert auction_result.payment_ends_at == auction.payment_ends_at
    assert auction_result.sponsored_starts_at == auction.sponsored_starts_at
    assert auction_result.sponsored_ends_at == auction.sponsored_ends_at
    assert auction_result.minimum_bid == auction.minimum_bid
    assert auction_result.sponsored_slots == auction.sponsored_slots


def test_get_auction_invalid_auction_id(
    session,
):
    """Test getting an auction with an invalid auction id"""

    with pytest.raises(NotFound) as e:
        auction_service.get_auction(
            db=session,
            auction_id=uuid4(),
        )

    assert e.value.message == "Auction not found"
