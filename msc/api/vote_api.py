from fastapi import APIRouter, Depends
from fastapi.requests import Request

from msc.dto.vote_dto import (
    CreateVoteInputDto,
    CheckVoteInputDto,
    CheckVoteOutputDto,
    CheckVoteOutputDebugDto,
)
from msc.services import vote_service

router = APIRouter()


@router.post("/votes")
def add_vote(
    request: Request,
    body: CreateVoteInputDto,
) -> str:
    """Endpoint for adding a voter"""

    vote_service.add_vote(
        server_id=body.server_id,
        client_ip=request.client.host,
    )

    return "success"


@router.get("/votes/check")
def check_vote_info(
    request: Request,
    query_params: CheckVoteInputDto = Depends(),
) -> CheckVoteOutputDto | CheckVoteOutputDebugDto:
    """Endpoint for checking if a voter has voted for a server in the last 24 hours"""

    response = vote_service.check_vote_info(
        server_id=query_params.server_id,
        client_ip=request.client.host,
    )

    if query_params.debug:
        return CheckVoteOutputDebugDto(
            has_voted=response.has_voted,
            last_vote=response.last_vote,
            time_left_ms=response.time_left_ms,
            client_ip=request.client.host,
        )
    else:
        return CheckVoteOutputDto(
            has_voted=response.has_voted,
            last_vote=response.last_vote,
            time_left_ms=response.time_left_ms,
        )
