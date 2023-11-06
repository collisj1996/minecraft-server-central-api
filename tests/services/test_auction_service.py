import math
from datetime import datetime, timedelta
from uuid import uuid4

import freezegun
import pytest

from msc.constants import MINIMUM_BID_DEFAULT, SPONSORED_SLOTS_DEFAULT, BidPaymentStatus
from msc.errors import NotFound, Unauthorized
from msc.jobs.jobs import persisted_scheduler
from msc.models import Auction, AuctionBid, Server, Sponsor, User
from msc.services import auction_service, server_service


def test_create_auction(
    session,
):
    """Tests creating an auction"""

    # using freezegun set the time to 1st of Jan 2021
    with freezegun.freeze_time(datetime(2021, 1, 1)):
        auction = auction_service.create_auction(
            db=session,
            sponsored_year=2021,
            sponsored_month=2,
        )

    assert auction
    assert auction.bidding_starts_at == datetime(2021, 1, 18, 0, 0)
    assert auction.bidding_ends_at == datetime(2021, 1, 28, 12, 0)
    assert auction.payment_starts_at == datetime(2021, 1, 28, 12, 1)
    assert auction.payment_ends_at == datetime(2021, 1, 31, 0, 0)
    assert auction.sponsored_starts_at == datetime(2021, 2, 1)
    assert auction.sponsored_ends_at == datetime(2021, 2, 28, 23, 59, 59, 999999)
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


@pytest.mark.nomockgeteligibility
def test_bid_on_auction_eligibility(
    session,
    user_jack: User,
    server_colcraft: Server,
    auction_inside_bidding_period: Auction,
):
    # not eligible for auction

    server_colcraft.uptime = 89
    server_colcraft.created_at = datetime.utcnow() - timedelta(days=29)

    session.commit()

    with pytest.raises(auction_service.ServerNotEligibleForAuctionBadRequest) as e:
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_inside_bidding_period.id,
            user_id=user_jack.id,
            server_id=server_colcraft.id,
            amount=100,
        )

    assert e.value.message == "This server is not eligible for sponsored auction"

    server_colcraft.uptime = 90
    server_colcraft.created_at = datetime.utcnow() - timedelta(days=30)

    session.commit()

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=user_jack.id,
        server_id=server_colcraft.id,
        amount=100,
    )

    server_colcraft.uptime = 91
    server_colcraft.created_at = datetime.utcnow() - timedelta(days=31)

    session.commit()

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=user_jack.id,
        server_id=server_colcraft.id,
        amount=200,
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

    assert e.value.message == "Bid amount must be greater than your current bid"


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
        == 1
    )

    assert (
        session.query(AuctionBid)
        .filter(AuctionBid.auction_id == auction_inside_bidding_period.id)
        .filter(AuctionBid.user_id == user_jack.id)
        .filter(AuctionBid.server_id == server_colcraft.id)
        .one_or_none()
        .amount
        == 300
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

    assert auction_result.auction
    assert auction_result.auction.id == auction.id
    assert auction_result.auction.bidding_starts_at == auction.bidding_starts_at
    assert auction_result.auction.bidding_ends_at == auction.bidding_ends_at
    assert auction_result.auction.payment_starts_at == auction.payment_starts_at
    assert auction_result.auction.payment_ends_at == auction.payment_ends_at
    assert auction_result.auction.sponsored_starts_at == auction.sponsored_starts_at
    assert auction_result.auction.sponsored_ends_at == auction.sponsored_ends_at
    assert auction_result.auction.minimum_bid == auction.minimum_bid
    assert auction_result.auction.sponsored_slots == auction.sponsored_slots


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


def test_no_more_than_one_current_auction(session):
    """Test that there can not be more than one current auction"""

    auction_service.create_auction(
        db=session,
        sponsored_year=2021,
        sponsored_month=1,
        is_current_auction=False,
    )

    auction_service.create_auction(
        db=session,
        sponsored_year=2021,
        sponsored_month=2,
        is_current_auction=False,
    )

    auction_service.create_auction(
        db=session,
        sponsored_year=2021,
        sponsored_month=3,
        is_current_auction=True,
    )

    with pytest.raises(auction_service.OnlyOneCurrentAuctionBadRequest) as e:
        auction_service.create_auction(
            db=session,
            sponsored_year=2021,
            sponsored_month=4,
            is_current_auction=True,
        )


def test_change_current_auction(session):
    """Test changing the current auction"""
    auction_1 = auction_service.create_auction(
        db=session,
        sponsored_year=2021,
        sponsored_month=1,
        is_current_auction=True,
    )

    auction_2 = auction_service.create_auction(
        db=session,
        sponsored_year=2021,
        sponsored_month=2,
        is_current_auction=False,
    )

    updated_auction = auction_service.change_current_auction(
        db=session, auction_id=auction_2.id
    )

    assert updated_auction.auction.is_current_auction == True
    assert auction_1.is_current_auction == False


def test_change_current_auction_no_current_auction(session):
    """Test changing the current auction when there is no current auction"""
    auction_1 = auction_service.create_auction(
        db=session,
        sponsored_year=2021,
        sponsored_month=1,
        is_current_auction=False,
    )

    updated_auction = auction_service.change_current_auction(
        db=session, auction_id=auction_1.id
    )

    assert updated_auction.auction.is_current_auction == True


def test_get_current_auction_with_bids(
    session,
    auction_with_bids: Auction,
    server_colcraft: Server,
    server_hypixel: Server,
):
    get_current_auction = auction_service.get_current_auction(
        db=session,
    )

    assert get_current_auction.auction.id == auction_with_bids.id
    assert (
        get_current_auction.auction.sponsored_year == auction_with_bids.sponsored_year
    )
    assert (
        get_current_auction.auction.sponsored_month == auction_with_bids.sponsored_month
    )

    assert len(get_current_auction.bids) == 10

    assert get_current_auction.bids[0].amount == 70000
    assert get_current_auction.bids[1].amount == 2100
    assert get_current_auction.bids[2].amount == 1050
    assert get_current_auction.bids[3].amount == 1000
    assert get_current_auction.bids[4].amount == 650
    assert get_current_auction.bids[5].amount == 600
    assert get_current_auction.bids[5].server_id == server_colcraft.id
    assert get_current_auction.bids[6].amount == 550
    assert get_current_auction.bids[6].server_id == server_hypixel.id
    assert get_current_auction.bids[7].amount == 525
    assert get_current_auction.bids[8].amount == 500
    assert get_current_auction.bids[9].amount == 400


def test_get_historical_auctions(
    session,
    user_jack: User,
    user_alan: User,
    server_colcraft: Server,
    server_hypixel: Server,
):
    """Test getting all non current auctions"""

    with freezegun.freeze_time(datetime(2023, 9, 24)):
        # create one auction
        auction_2023_10 = auction_service.create_auction(
            db=session,
            sponsored_year=2023,
            sponsored_month=10,
            is_current_auction=True,
        )

        # add some bids to the auction
        # user_jack bids for server_colcraft for auction_2023_10 for 100
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_2023_10.id,
            user_id=user_jack.id,
            server_id=server_colcraft.id,
            amount=100,
        )

        # user_jack bids for server_colcraft for auction_2023_10 for 200
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_2023_10.id,
            user_id=user_jack.id,
            server_id=server_colcraft.id,
            amount=125,
        )

        # user_alan bids for server_hypixel for auction_2023_10 for 200
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_2023_10.id,
            user_id=user_alan.id,
            server_id=server_hypixel.id,
            amount=500,
        )

        auction_service.unset_current_auction(db=session)

    with freezegun.freeze_time(datetime(2023, 10, 24)):
        # create another auction
        auction_2023_11 = auction_service.create_auction(
            db=session,
            sponsored_year=2023,
            sponsored_month=11,
            is_current_auction=False,
        )

        auction_service.change_current_auction(
            db=session,
            auction_id=auction_2023_11.id,
        )

        # user_jack bids for server_colcraft for auction_2023_11 for 100
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_2023_11.id,
            user_id=user_jack.id,
            server_id=server_colcraft.id,
            amount=100,
        )

        # user_jack bids for server_colcraft for auction_2023_11 for 200
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_2023_11.id,
            user_id=user_jack.id,
            server_id=server_colcraft.id,
            amount=700,
        )

        # user_alan bids for server_hypixel for auction_2023_11 for 200
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_2023_11.id,
            user_id=user_alan.id,
            server_id=server_hypixel.id,
            amount=600,
        )

        auction_service.unset_current_auction(db=session)

        # set all bids to paid
        for bid in session.query(AuctionBid).all():
            bid.payment_status = BidPaymentStatus.PAID

    session.commit()

    # get all auctions
    auctions = auction_service.get_historical_auctions(db=session)

    assert len(auctions) == 2

    # assert auction_2023_11 first, since it is the most recent
    assert auctions[0].auction.id == auction_2023_11.id
    assert auctions[0].auction.sponsored_year == 2023
    assert auctions[0].auction.sponsored_month == 11
    assert auctions[0].auction.is_current_auction == False

    # assert auction_2023_10 second, since it is the least recent
    assert auctions[1].auction.id == auction_2023_10.id
    assert auctions[1].auction.sponsored_year == 2023
    assert auctions[1].auction.sponsored_month == 10
    assert auctions[1].auction.is_current_auction == False

    # assert auction_2023_10 bids
    assert len(auctions[1].bids) == 2

    # assert auction_2023_10 bids, highest bid first
    assert auctions[1].bids[0].amount == 500
    assert auctions[1].bids[0].user_id == user_alan.id
    assert auctions[1].bids[0].server_id == server_hypixel.id

    assert auctions[1].bids[1].amount == 125
    assert auctions[1].bids[1].user_id == user_jack.id
    assert auctions[1].bids[1].server_id == server_colcraft.id

    # assert auction_2023_11 bids
    assert len(auctions[0].bids) == 2

    # assert auction_2023_11 bids, highest bid first
    assert auctions[0].bids[0].amount == 700
    assert auctions[0].bids[0].user_id == user_jack.id
    assert auctions[0].bids[0].server_id == server_colcraft.id

    assert auctions[0].bids[1].amount == 600
    assert auctions[0].bids[1].user_id == user_alan.id
    assert auctions[0].bids[1].server_id == server_hypixel.id


def test_get_historical_auctions_pagination(
    session,
    historical_auctions_with_bids: list[Auction],
):
    """Test getting all non current auctions with pagination"""

    page_size = 8
    page = 1
    num_pages = math.ceil(len(historical_auctions_with_bids) / page_size)

    # order historical auctions with bids by most recent first
    historical_auctions_with_bids.sort(
        key=lambda x: x.sponsored_starts_at, reverse=True
    )

    for i in range(1, num_pages + 1):
        print("Page: ", page)

        response = auction_service.get_historical_auctions(
            db=session,
            page=page,
            per_page=page_size,
        )

        # assert the correct number of auctions are returned for each page
        if page == num_pages:  # last page
            assert len(response) == len(historical_auctions_with_bids) % page_size
        else:
            assert len(response) == page_size

        page += 1

        # assert the auctions are ordered by most recent first
        for j in range(1, len(response) + 1):
            index = (i - 1) * page_size + j - 1
            assert response[j - 1].auction.id == historical_auctions_with_bids[index].id

        previous_bid = None
        # assert the bids are ordered by highest bid first
        for auction_info in response:
            for bid in auction_info.bids:
                if previous_bid:
                    assert bid.amount <= previous_bid.amount
                previous_bid = bid

            previous_bid = None


def test_start_payment_phase(
    session,
    auction_with_bids: Auction,
    ten_more_servers,
):
    """Test starting the payment phase of an auction"""

    # add more bids
    with freezegun.freeze_time(datetime(2020, 12, 19)):
        for index, server in enumerate(ten_more_servers["servers_list"]):
            auction_service.add_auction_bid(
                db=session,
                auction_id=auction_with_bids.id,
                user_id=server.user_id,
                server_id=server.id,
                amount=570 + index,
            )

    with freezegun.freeze_time(datetime(2020, 12, 28, 12, 1)):
        auction_service.start_payment_phase(
            db=session,
        )

    with freezegun.freeze_time(datetime(2020, 12, 28, 12, 2)):
        auction = auction_service.get_current_auction(
            db=session,
        )

        # assert first x=sponsored_slots bids have status of Awaiting Response
        for bid in auction.bids[: auction.auction.sponsored_slots]:
            assert bid.payment_status == BidPaymentStatus.AWAITING_RESPONSE

        # assert the rest of the bids have status of Standby
        for bid in auction.bids[auction.auction.sponsored_slots :]:
            assert bid.payment_status == BidPaymentStatus.STANDBY


def test_distinct_bid_amount(
    session,
    server_colcraft: Server,
    server_hypixel: Server,
    auction_inside_bidding_period: Auction,
):
    """Test that each bid is a distinct amount"""

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=server_colcraft.user_id,
        server_id=server_colcraft.id,
        amount=100,
    )

    with pytest.raises(auction_service.InvalidBidAmount) as e:
        auction_service.add_auction_bid(
            db=session,
            auction_id=auction_inside_bidding_period.id,
            user_id=server_hypixel.user_id,
            server_id=server_hypixel.id,
            amount=100,
        )

    assert e.value.message == "Bid amount must be unique"


def test_set_bid_payment_status(
    session,
    server_colcraft: Server,
    auction_inside_bidding_period: Auction,
):
    """Test setting the payment status of a bid"""

    # add a bid
    bid = auction_service.add_auction_bid(
        db=session,
        auction_id=auction_inside_bidding_period.id,
        user_id=server_colcraft.user_id,
        server_id=server_colcraft.id,
        amount=100,
    )

    # assert the bid has None as the payment status
    assert bid.payment_status == None

    # set the payment status of the bid to Paid
    auction_service.set_bid_payment_status(
        db=session,
        bid_id=bid.id,
        payment_status=BidPaymentStatus.PAID,
    )

    # assert the bid has the correct payment status
    assert bid.payment_status == BidPaymentStatus.PAID


def test_create_current_auction(session):
    """Test creating the current auction"""

    with freezegun.freeze_time(datetime(2020, 11, 1)):
        auction = auction_service.create_current_auction(db=session)
        assert auction.sponsored_year == 2020
        assert auction.sponsored_month == 12

        assert auction.is_current_auction == True

    with freezegun.freeze_time(datetime(2020, 12, 1)):
        auction_1 = auction_service.create_current_auction(db=session)
        assert auction_1.sponsored_year == 2021
        assert auction_1.sponsored_month == 1

        assert auction.is_current_auction == False
        assert auction_1.is_current_auction == True

    with freezegun.freeze_time(datetime(2021, 1, 1)):
        auction_2 = auction_service.create_current_auction(db=session)
        assert auction_2.sponsored_year == 2021
        assert auction_2.sponsored_month == 2

    assert auction.is_current_auction == False
    assert auction_1.is_current_auction == False
    assert auction_2.is_current_auction == True


def test_populate_sponsored_servers_and_get_them(
    session,
    server_colcraft: Server,
    auction_with_bids: Auction,
    ten_more_servers,
):
    """Tests that the populate_sponsored_servers method works correctly"""

    # add more bids
    with freezegun.freeze_time(datetime(2020, 12, 19)):
        sponsor = Sponsor(
            user_id=server_colcraft.user_id,
            server_id=server_colcraft.id,
            slot=1,
            year=2020,
            month=12,
        )

        session.add(sponsor)
        session.commit()

        # get sponsored servers
        sponsored_servers = server_service.get_sponsored_servers(
            db=session,
        )

        # assert there are no sponsored servers
        assert len(sponsored_servers) == 1

        # assert the sponsored server is the server that was sponsored
        assert sponsored_servers[0].server.id == server_colcraft.id

        for index, server in enumerate(ten_more_servers["servers_list"]):
            auction_service.add_auction_bid(
                db=session,
                auction_id=auction_with_bids.id,
                user_id=server.user_id,
                server_id=server.id,
                amount=570 + index,
            )

    with freezegun.freeze_time(datetime(2020, 12, 28, 12, 1)):
        auction_service.start_payment_phase(
            db=session,
        )

        current_auction = auction_service.get_current_auction(
            db=session,
        )

        for bid in current_auction.bids:
            if bid.payment_status == BidPaymentStatus.AWAITING_RESPONSE:
                bid.payment_status = BidPaymentStatus.PAID

        session.commit()

    with freezegun.freeze_time(datetime(2020, 12, 31, 12, 0)):
        auction_service.populate_sponsored_servers(
            db=session,
        )

        # get sponsored servers, should still be previous sponsored servers
        sponsored_servers = server_service.get_sponsored_servers(
            db=session,
        )

        # assert there are no sponsored servers
        assert len(sponsored_servers) == 1

        # assert the sponsored server is the server that was sponsored
        assert sponsored_servers[0].server.id == server_colcraft.id

    with freezegun.freeze_time(datetime(2021, 1, 1, 1)):
        # get sponsored servers, should be the new sponsored servers
        sponsored_servers = server_service.get_sponsored_servers(
            db=session,
        )

        assert len(sponsored_servers) == 10

        # assert the sponsored servers have the correct order with relation to the bids
        for i in range(0, len(sponsored_servers)):
            assert sponsored_servers[i].server.id == current_auction.bids[i].server_id

        sponsors = (
            session.query(Sponsor)
            .filter(
                Sponsor.year == "2021",
                Sponsor.month == "1",
            )
            .all()
        )

        # assert the order of sponsored servers matches sponsor_slot
        for index, server in enumerate(sponsored_servers):
            assert sponsors[index].server_id == server.server.id
            assert sponsors[index].slot == index + 1


@pytest.mark.disable_mock_tasks
def test_auction_jobs_scheduled(session):
    """Tests that the scheduled jobs for starting the pay_phase and populating the sponsored servers
    are in fact scheduled and at the correct time"""

    persisted_scheduler.start()

    current_auction = auction_service.create_current_auction(
        db=session,
    )

    jobs = persisted_scheduler.get_jobs()

    for job in jobs:
        if job.name == "start_payment_phase_task":
            assert str(job.next_run_time).split("+")[0] == str(
                current_auction.payment_starts_at
            )

        if job.name == "populate_sponsored_servers_task":
            assert str(job.next_run_time).split("+")[0] == str(
                current_auction.sponsored_starts_at - timedelta(hours=12)
            )
