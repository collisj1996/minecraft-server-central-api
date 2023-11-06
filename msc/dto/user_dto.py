from uuid import UUID

from msc.dto.base import BaseDto


class UserDto(BaseDto):
    user_id: str
    username: str
    email: str


class UserAddInputDto(BaseDto):
    user_id: UUID
    username: str
    email: str


class ChangePasswordInput(BaseDto):
    previous_password: str
    proposed_password: str
