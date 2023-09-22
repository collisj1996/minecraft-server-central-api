from uuid import UUID

from msc.dto.base import BaseDto
from msc.dto.custom_types import DateTimeUTC


class CreateVoteInputDto(BaseDto):
    server_id: UUID
    minecraft_username: str


class CheckVoteInputDto(BaseDto):
    server_id: UUID
    debug: bool = False


class CheckVoteOutputDto(BaseDto):
    has_voted: bool
    last_vote: DateTimeUTC
    time_left_ms: int


class CheckVoteOutputDebugDto(CheckVoteOutputDto):
    client_ip: str
