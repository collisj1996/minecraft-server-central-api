from uuid import UUID
from typing import Optional

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
    last_vote: Optional[DateTimeUTC] = None
    time_left_ms: Optional[int] = None
    client_ip: str  # TODO: Remove this
