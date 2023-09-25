from fastapi import APIRouter
from fastapi.requests import Request

from msc.dto.user_dto import UserAddInputDto
from msc.services import user_service

router = APIRouter()


@router.post("/users")
def add_user(
    request: Request,
    body: UserAddInputDto,
):
    """Endpoint for creating a user"""

    # TODO: Add auth check

    user = user_service.add_user(
        user_id=body.user_id,
        username=body.username,
        email=body.email,
    )

    return {"user_id": user.id}
