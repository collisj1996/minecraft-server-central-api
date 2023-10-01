import pytest
from datetime import datetime, timedelta
from msc.models import Auction, Server
import freezegun

from msc.services import auction_service


@pytest.fixture
def auction(session):
    """Returns a default auction"""

    MONTH = 1
    YEAR = 2021

    auction: Auction = auction_service.create_auction(
        db=session,
        sponsored_year=YEAR,
        sponsored_month=MONTH,
        is_current_auction=True,
    )

    return auction


@pytest.fixture
def auction_inside_bidding_period(auction):
    """Returns the time bidding starts"""

    with freezegun.freeze_time(datetime(2020, 12, 21)):
        yield auction


@pytest.fixture
def auction_before_bidding_period(auction):
    """Returns the time bidding starts"""

    with freezegun.freeze_time(datetime(2020, 12, 15)):
        yield auction


@pytest.fixture
def auction_after_bidding_period(auction):
    """Returns the time bidding starts"""

    with freezegun.freeze_time(datetime(2021, 12, 30, 12)):
        yield auction


@pytest.fixture
def auction_with_bids(
    session,
    auction_inside_bidding_period,
    ten_servers,
    server_colcraft: Server,
    server_hypixel: Server,
):
    """Returns an auction with many bids from 10 servers"""

    servers = ten_servers["servers_list"]
    # users = ten_servers["users_list"]
    # servers_map = ten_servers["servers_map"]
    # users_map = ten_servers["users_map"]

    auction = auction_inside_bidding_period

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[0].user_id,
        server_id=servers[0].id,
        amount=100,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[0].user_id,
        server_id=servers[0].id,
        amount=200,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[1].user_id,
        server_id=servers[1].id,
        amount=200,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[2].user_id,
        server_id=servers[2].id,
        amount=69000,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[2].user_id,
        server_id=servers[2].id,
        amount=70000,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[3].user_id,
        server_id=servers[3].id,
        amount=500,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[4].user_id,
        server_id=servers[4].id,
        amount=500,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[5].user_id,
        server_id=servers[5].id,
        amount=650,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[6].user_id,
        server_id=servers[6].id,
        amount=1000,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[7].user_id,
        server_id=servers[7].id,
        amount=400,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[8].user_id,
        server_id=servers[8].id,
        amount=2000,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[8].user_id,
        server_id=servers[8].id,
        amount=2100,
    )

    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=servers[9].user_id,
        server_id=servers[9].id,
        amount=1000,
    )

    # add additoinal bids to colcraft
    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=server_colcraft.user_id,
        server_id=server_colcraft.id,
        amount=600,
    )

    # add additoinal bids to hypixel
    auction_service.add_auction_bid(
        db=session,
        auction_id=auction.id,
        user_id=server_hypixel.user_id,
        server_id=server_hypixel.id,
        amount=550,
    )

    return auction


@pytest.fixture
def historical_auctions_with_bids(session, ten_servers):
    servers = ten_servers["servers_list"]

    YEAR = 2021

    auctions = []

    for i in range(1, 30):
        month = i % 12

        if month == 0:
            month = 12

        auction: Auction = auction_service.create_auction(
            db=session,
            sponsored_year=YEAR,
            sponsored_month=month,
            is_current_auction=True,
        )

        with freezegun.freeze_time(auction.bidding_starts_at + timedelta(days=1)):
            for index, server in enumerate(servers):
                auction_service.add_auction_bid(
                    db=session,
                    auction_id=auction.id,
                    user_id=server.user_id,
                    server_id=server.id,
                    amount=100 * (index + 1),
                )

        auction_service.unset_current_auction(db=session)

        auctions.append(auction)

        if i % 12 == 0:
            YEAR += 1

    return auctions
