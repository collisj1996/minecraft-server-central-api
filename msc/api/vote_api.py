import logging

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.orm import Session

from msc.database import get_db
from msc.dto.vote_dto import CheckVoteInputDto, CheckVoteOutputDto, CreateVoteInputDto
from msc.services import vote_service
from msc.utils import api_utils

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/votes")
def add_vote(
    request: Request,
    body: CreateVoteInputDto,
    db: Session = Depends(get_db),
) -> str:
    """Endpoint for adding a voter"""

    client_ip = api_utils.get_client_ip(request)

    # TODO: Add error handling for no client IP

    vote_service.add_vote(
        db=db,
        server_id=body.server_id,
        client_ip=client_ip,
        minecraft_username=body.minecraft_username,
    )

    return "success"


@router.get("/votes/check")
def check_vote_info(
    request: Request,
    query_params: CheckVoteInputDto = Depends(),
    db: Session = Depends(get_db),
) -> CheckVoteOutputDto:
    """Endpoint for checking if a voter has voted for a server in the last 24 hours"""

    client_ip = api_utils.get_client_ip(request)

    # TODO: Add error handling for no client IP

    response = vote_service.check_vote_info(
        db=db,
        server_id=query_params.server_id,
        client_ip=client_ip,
    )

    return CheckVoteOutputDto(
        has_voted=response.has_voted,
        last_vote=response.last_vote,
        time_left_ms=response.time_left_ms,
        client_ip=client_ip,
    )
