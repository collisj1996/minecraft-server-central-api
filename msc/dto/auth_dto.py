from msc.dto.base import BaseDto
from typing import Optional


class GetTokenInputDto(BaseDto):
    code: str
    redirect_url: Optional[str] = "https://minecraftservercentral.com"


class GetTokenOutputDto(BaseDto):
    id_token: str
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class RefreshTokenInputDto(BaseDto):
    refresh_token: str
