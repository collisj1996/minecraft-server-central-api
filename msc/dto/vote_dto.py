from uuid import UUID

from msc.dto.base import BaseDto


class CreateVoteInputDto(BaseDto):
    server_id: UUID
    minecraft_username: str
