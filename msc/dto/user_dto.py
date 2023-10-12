from msc.dto.base import BaseDto
from uuid import UUID


class UserDto(BaseDto):
    user_id: str
    username: str
    email: str


class UserAddInputDto(BaseDto):
    user_id: UUID
    username: str
    email: str
