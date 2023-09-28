from uuid import UUID
from typing import Optional

from msc.models import Auction, AuctionBid
from msc.dto.base import BaseDto
from msc.dto.custom_types import DateTimeUTC
from msc.services.auction_service import GetAuctionInfo


class AuctionDto(BaseDto):
    id: UUID
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

    @classmethod
    def from_service(cls, auction_bid: AuctionBid):
        return cls(
            auction_id=auction_bid.auction_id,
            user_id=auction_bid.user_id,
            server_id=auction_bid.server_id,
            server_name=auction_bid.server_name,
            amount=auction_bid.amount,
            created_at=auction_bid.created_at,
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
    pass
    # TODO: Add pagination


class AuctionCreateInputDto(BaseDto):
    bidding_starts_at: DateTimeUTC
    bidding_ends_at: DateTimeUTC
    payment_starts_at: DateTimeUTC
    payment_ends_at: DateTimeUTC
    sponsored_starts_at: DateTimeUTC
    sponsored_ends_at: DateTimeUTC
    minimum_bid: Optional[int]
    sponsored_slots: Optional[int]


class AuctionBidCreateInputDto(BaseDto):
    auction_id: UUID
    user_id: UUID
    server_id: UUID
    server_name: str
    amount: int
