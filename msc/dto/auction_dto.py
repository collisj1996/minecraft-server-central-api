from typing import Optional
from uuid import UUID

from pydantic import conint

from msc.constants import (
    DEFAULT_AUCTION_PAGE,
    DEFAULT_AUCTION_PAGE_SIZE,
    MAX_AUCTIONS_PAGE_SIZE,
    MINIMUM_BID_DEFAULT,
    SPONSORED_SLOTS_DEFAULT,
    BidPaymentStatus,
)
from msc.dto.base import BaseDto
from msc.dto.custom_types import DateTimeUTC
from msc.models import Auction, AuctionBid
from msc.services.auction_service import GetAuctionInfo


class AuctionDto(BaseDto):
    id: UUID
    sponsored_year: int
    sponsored_month: int
    bidding_starts_at: DateTimeUTC
    bidding_ends_at: DateTimeUTC
    payment_starts_at: DateTimeUTC
    payment_ends_at: DateTimeUTC
    sponsored_starts_at: DateTimeUTC
    sponsored_ends_at: DateTimeUTC
    minimum_bid: int
    sponsored_slots: int

    @classmethod
    def from_service(cls, auction: Auction):
        return cls(
            id=auction.id,
            sponsored_year=auction.sponsored_year,
            sponsored_month=auction.sponsored_month,
            bidding_starts_at=auction.bidding_starts_at,
            bidding_ends_at=auction.bidding_ends_at,
            payment_starts_at=auction.payment_starts_at,
            payment_ends_at=auction.payment_ends_at,
            sponsored_starts_at=auction.sponsored_starts_at,
            sponsored_ends_at=auction.sponsored_ends_at,
            minimum_bid=auction.minimum_bid,
            sponsored_slots=auction.sponsored_slots,
        )


class AuctionBidDto(BaseDto):
    auction_id: UUID
    user_id: UUID
    server_id: UUID
    server_name: str
    amount: int
    created_at: DateTimeUTC
    payment_status: Optional[BidPaymentStatus] = None

    @classmethod
    def from_service(cls, auction_bid: AuctionBid):
        return cls(
            auction_id=auction_bid.auction_id,
            user_id=auction_bid.user_id,
            server_id=auction_bid.server_id,
            server_name=auction_bid.server_name,
            amount=auction_bid.amount,
            created_at=auction_bid.created_at,
            payment_status=auction_bid.payment_status,
        )


class AuctionGetInputDto(BaseDto):
    auction_id: UUID


class AuctionGetOutputDto(BaseDto):
    auction: AuctionDto
    bids: list[AuctionBidDto]

    @classmethod
    def from_service(cls, auction_info: GetAuctionInfo):
        return cls(
            auction=AuctionDto.from_service(auction_info.auction),
            bids=[AuctionBidDto.from_service(bid) for bid in auction_info.bids],
        )


class AuctionsGetInputDto(BaseDto):
    include_current: Optional[bool] = False
    page: Optional[int] = DEFAULT_AUCTION_PAGE
    page_size: Optional[
        conint(ge=5, le=MAX_AUCTIONS_PAGE_SIZE)
    ] = DEFAULT_AUCTION_PAGE_SIZE


class AuctionCreateInputDto(BaseDto):
    sponsored_year: int
    sponsored_month: int
    minimum_bid: Optional[int] = MINIMUM_BID_DEFAULT
    sponsored_slots: Optional[int] = SPONSORED_SLOTS_DEFAULT


class AuctionCurrentCreateInputDto(BaseDto):
    minimum_bid: Optional[int] = MINIMUM_BID_DEFAULT
    sponsored_slots: Optional[int] = SPONSORED_SLOTS_DEFAULT


class AuctionBidCreateInputDto(BaseDto):
    server_id: UUID
    amount: int


class AuctionBidSetPaymentStatusInputDto(BaseDto):
    payment_status: BidPaymentStatus
