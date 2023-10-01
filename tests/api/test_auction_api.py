import math

from fastapi.testclient import TestClient

from msc.config import config
from msc.models import Auction, User

from .utils import get_auth_header, get_response_body


def test_create_auction(
    session,
    test_client: TestClient,
    user_jack: User,
):
    config.development_mode = True
    response = test_client.post(
        "/auctions",
        headers=get_auth_header(user_jack.id),
        json={
            "sponsored_year": 2021,
            "sponsored_month": 1,
        },
    )
    assert response.status_code == 200

    body = get_response_body(response)

    assert body["sponsored_year"] == 2021
    assert body["sponsored_month"] == 1
    assert body["bidding_starts_at"] == "2020-12-18T00:00:00.000000Z"
    assert body["bidding_ends_at"] == "2020-12-28T12:00:00.000000Z"
    assert body["payment_starts_at"] == "2020-12-28T12:01:00.000000Z"
    assert body["payment_ends_at"] == "2020-12-31T00:00:00.000000Z"
    assert body["sponsored_starts_at"] == "2021-01-01T00:00:00.000000Z"
    assert body["sponsored_ends_at"] == "2021-01-31T23:59:59.999999Z"
    assert body["minimum_bid"] == 10
    assert body["sponsored_slots"] == 10


def test_get_auctions(
    session,
    test_client: TestClient,
    historical_auctions_with_bids: list[Auction],
    user_jack: User,
):
    """Test getting auctions"""
    config.development_mode = True

    page_size = 8
    page = 1
    num_pages = math.ceil(len(historical_auctions_with_bids) / page_size)

    # order historical auctions with bids by most recent first
    historical_auctions_with_bids.sort(
        key=lambda x: x.sponsored_starts_at, reverse=True
    )

    for i in range(1, num_pages + 1):
        response = test_client.get(
            "/auctions",
            headers=get_auth_header(user_jack.id),
            params={
                "include_current_auction": False,
                "page": page,
                "page_size": page_size,
            },
        )

        body = response.json()

        # assert the correct number of auctions are returned for each page
        if page == num_pages:  # last page
            assert len(body) == len(historical_auctions_with_bids) % page_size
        else:
            assert len(body) == page_size

        page += 1

        # # assert the auctions are ordered by most recent first
        for j in range(1, len(body) + 1):
            index = (i - 1) * page_size + j - 1
            assert body[j - 1]["auction"]["id"] == str(
                historical_auctions_with_bids[index].id
            )
