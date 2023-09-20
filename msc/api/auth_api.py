from fastapi import APIRouter, Depends
from fastapi.requests import Request

from msc.dto.auth_dto import RefreshTokenInputDto, GetTokenInputDto, GetTokenOutputDto

from msc.services import auth_service

router = APIRouter()


@router.get("/auth/get_token")
def get_token(
    request: Request,
    query_params: GetTokenInputDto = Depends(),
):
    """Endpoint for getting a token"""

    response = auth_service.get_token(code=query_params.code, redirect_url=query_params.redirect_url,)

    return GetTokenOutputDto.parse_obj(response)


@router.post("/auth/refresh_token")
def refresh_token(
    request: Request,
    query_params: RefreshTokenInputDto = Depends(),
):
    """Endpoint for refreshing a token"""

    token = auth_service.refresh_token(refresh_token=query_params.refresh_token,)

    return token