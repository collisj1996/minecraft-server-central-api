import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.orm import Session

from msc.database import get_db
from msc.dto.auction_dto import (
    AuctionBidCreateInputDto,
    AuctionBidDto,
    AuctionCreateInputDto,
    AuctionDto,
    AuctionGetInputDto,
    AuctionGetOutputDto,
    AuctionsGetInputDto,
)
from msc.services import auction_service
from msc.utils.api_utils import admin_required, auth_required

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/auctions")
@admin_required
def create_auction(
    request: Request,
    body: AuctionCreateInputDto,
    db: Session = Depends(get_db),
) -> AuctionDto:
    """Endpoint for adding a voter"""

    auction = auction_service.create_auction(
        db=db,
        sponsored_year=body.sponsored_year,
        sponsored_month=body.sponsored_month,
        is_current_auction=body.is_current_auction,
    )

    return AuctionDto.from_service(auction)


@router.get("/auctions/current")
@auth_required
def get_current_auction(
    request: Request,
    db: Session = Depends(get_db),
) -> AuctionGetOutputDto:
    """Endpoint for getting the current auction"""

    auction_info = auction_service.get_current_auction(
        db=db,
    )

    return AuctionGetOutputDto.from_service(auction_info)


@router.patch("/auctions/{auction_id}/current")
@admin_required
def change_current_auction(
    request: Request,
    auction_id: str,
    db: Session = Depends(get_db),
) -> AuctionGetOutputDto:
    """Endpoint for changing the current auction"""

    auction_info = auction_service.change_current_auction(
        db=db,
        auction_id=UUID(auction_id),
    )

    return AuctionGetOutputDto.from_service(auction_info)


@router.get("/auctions/{auction_id}")
@auth_required
def get_auction(
    request: Request,
    auction_id: str,
    db: Session = Depends(get_db),
) -> AuctionGetOutputDto:
    """Endpoint for getting an auction"""

    auction_info = auction_service.get_auction(
        db=db,
        auction_id=UUID(auction_id),
    )

    return AuctionGetOutputDto.from_service(auction_info)


@router.get("/auctions")
@auth_required
def get_auctions(
    request: Request,
    query_params: AuctionsGetInputDto = Depends(),
    db: Session = Depends(get_db),
) -> list[AuctionGetOutputDto]:
    """Endpoint for getting auctions"""

    auctions = auction_service.get_auctions(
        db=db,
        include_current_auction=query_params.include_current,
        page=query_params.page,
        per_page=query_params.page_size,
    )

    return [AuctionGetOutputDto.from_service(auction) for auction in auctions]


@router.post("/auctions/{auction_id}/bid")
@auth_required
def create_bid(
    request: Request,
    auction_id: str,
    body: AuctionBidCreateInputDto,
    db: Session = Depends(get_db),
) -> AuctionBidDto:
    """Endpoint for adding a bid to an auction"""

    user_id = request.state.user_id

    auction_bid = auction_service.add_auction_bid(
        db=db,
        auction_id=auction_id,
        user_id=UUID(user_id),
        server_id=body.server_id,
        amount=body.amount,
    )

    return AuctionBidDto.from_service(auction_bid)


@router.get("/auctions/{auction_id}/servers/{server_id}/bid")
@auth_required
def get_bid(
    request: Request,
    auction_id: str,
    server_id: str,
    db: Session = Depends(get_db),
) -> AuctionBidDto:
    """Endpoint for adding a bid to an auction"""

    user_id = request.state.user_id

    auction_bid = auction_service.get_bid(
        db=db,
        user_id=UUID(user_id),
        auction_id=auction_id,
        server_id=server_id,
    )

    return AuctionBidDto.from_service(auction_bid)


@router.get("/auctions/{auction_id}/bids")
@auth_required
def get_bids(
    request: Request,
    auction_id: str,
    db: Session = Depends(get_db),
) -> list[AuctionBidDto]:
    """Endpoint for getting all bids for an auction"""

    # TODO

    return []
