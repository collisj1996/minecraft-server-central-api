import pytest
from datetime import datetime
from msc.models import Auction
import freezegun

from msc.services import auction_service


@pytest.fixture
def auction(session):
    """Returns a default auction"""

    auction: Auction = auction_service.create_auction(
        db=session,
        bidding_starts_at=datetime(2021, 1, 18),
        bidding_ends_at=datetime(2021, 1, 28),
        payment_starts_at=datetime(2021, 1, 29),
        payment_ends_at=datetime(2021, 1, 30),
        sponsored_starts_at=datetime(2021, 2, 1),
        sponsored_ends_at=datetime(2021, 2, 28),
    )

    return auction


@pytest.fixture
def auction_inside_bidding_period(auction):
    """Returns the time bidding starts"""

    with freezegun.freeze_time(datetime(2021, 1, 19)):
        yield auction


@pytest.fixture
def auction_before_bidding_period(auction):
    """Returns the time bidding starts"""

    with freezegun.freeze_time(datetime(2021, 1, 17)):
        yield auction


@pytest.fixture
def auction_after_bidding_period(auction):
    """Returns the time bidding starts"""

    with freezegun.freeze_time(datetime(2021, 1, 29)):
        yield auction
