from fastapi import APIRouter, Depends
from fastapi.requests import Request
import logging

from msc.dto.vote_dto import (
    CreateVoteInputDto,
    CheckVoteInputDto,
    CheckVoteOutputDto,
)
from msc.services import vote_service

router = APIRouter()

logger = logging.getLogger(__name__)


def _get_client_ip(request):
    forwarded = request.headers["forwarded"]

    # Split the header into individual parameters
    header_parts = forwarded.split(";")

    # Create a dictionary to store the parsed values
    parsed_forwarded = {}

    # Loop through the parameters and parse them
    for part in header_parts:
        key, value = part.split("=")
        parsed_forwarded[key.strip()] = value.strip()

    # Extract individual components
    by = parsed_forwarded.get("by", None)
    for_ip = parsed_forwarded.get("for", None)
    host = parsed_forwarded.get("host", None)
    proto = parsed_forwarded.get("proto", None)

    return for_ip


@router.post("/votes")
def add_vote(
    request: Request,
    body: CreateVoteInputDto,
) -> str:
    """Endpoint for adding a voter"""

    client_ip = _get_client_ip(request)

    # TODO: Add error handling for no client IP

    vote_service.add_vote(
        server_id=body.server_id,
        client_ip=client_ip,
    )

    return "success"


@router.get("/votes/check")
def check_vote_info(
    request: Request,
    query_params: CheckVoteInputDto = Depends(),
) -> CheckVoteOutputDto:
    """Endpoint for checking if a voter has voted for a server in the last 24 hours"""

    client_ip = _get_client_ip(request)

    # TODO: Add error handling for no client IP

    response = vote_service.check_vote_info(
        server_id=query_params.server_id,
        client_ip=client_ip,
    )

    return CheckVoteOutputDto(
        has_voted=response.has_voted,
        last_vote=response.last_vote,
        time_left_ms=response.time_left_ms,
        client_ip=client_ip,
    )
