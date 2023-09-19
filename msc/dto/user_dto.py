from msc.dto.base import BaseDto


class UserAddInputDto(BaseDto):
    user_id: str
    username: str
    email: str
