from fastapi import APIRouter
from fastapi.requests import Request

from msc.dto.vote_dto import CreateVoteInputDto
from msc.services import vote_service

router = APIRouter()


@router.post("/votes")
def add_vote(
    request: Request,
    body: CreateVoteInputDto,
) -> str:
    """Endpoint for adding a voter"""

    # TODO: Add authentication here?

    vote_service.add_vote(
        server_id=body.server_id,
        client_ip=request.client.host,
    )

    return "success"
