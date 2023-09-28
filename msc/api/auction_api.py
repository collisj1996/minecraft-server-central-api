from fastapi import APIRouter, Depends
from fastapi.requests import Request
import logging
from uuid import UUID

from msc.dto.auction_dto import (
    AuctionCreateInputDto,
    AuctionDto,
    AuctionBidDto,
    AuctionGetInputDto,
    AuctionsGetInputDto,
    AuctionBidCreateInputDto,
    AuctionGetOutputDto,
)
from msc.services import auction_service
from msc.database import get_db
from sqlalchemy.orm import Session
from msc.utils.api_utils import auth_required, admin_required

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/auction")
@admin_required
def create_auction(
    request: Request,
    body: AuctionCreateInputDto,
    db: Session = Depends(get_db),
) -> AuctionDto:
    """Endpoint for adding a voter"""

    auction = auction_service.create_auction(
        db=db,
        bidding_starts_at=body.bidding_starts_at,
        bidding_ends_at=body.bidding_ends_at,
        payment_starts_at=body.payment_starts_at,
        payment_ends_at=body.payment_ends_at,
        sponsored_starts_at=body.sponsored_starts_at,
        sponsored_ends_at=body.sponsored_ends_at,
    )

    return AuctionDto.from_service(auction)


@router.get("/auction/{auction_id}")
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
) -> list[AuctionDto]:
    """Endpoint for getting auctions"""

    auctions = auction_service.get_auctions(
        db=db,
    )

    return [AuctionDto.from_service(auction) for auction in auctions]


@router.post("/auction/{auction_id}/bid")
@auth_required
def create_bid(
    request: Request,
    auction_id: str,
    body: AuctionBidCreateInputDto,
    db: Session = Depends(get_db),
) -> AuctionBidDto:
    """Endpoint for adding a voter"""

    auction_bid = auction_service.add_auction_bid(
        db=db,
        auction_id=auction_id,
        user_id=request.state.user_id,
        server_id=body.server_id,
        amount=body.amount,
    )

    return AuctionBidDto.from_service(auction_bid)
