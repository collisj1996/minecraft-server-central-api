from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.orm import Session

from msc.database import get_db
from msc.dto.user_dto import ChangePasswordInput, UserAddInputDto, UserDto
from msc.services import user_service
from msc.utils.api_utils import auth_required

router = APIRouter()


@router.post("/users")
def add_user(
    request: Request,
    body: UserAddInputDto,
    db: Session = Depends(get_db),
):
    """Endpoint for creating a user"""

    # TODO: Make this endpoint only triggerable by Step Function OR SNS

    user = user_service.add_user(
        db=db,
        user_id=body.user_id,
        username=body.username,
        email=body.email,
    )

    return {"user_id": user.id}


@router.get("/users")
@auth_required
def get_my_user(
    request: Request,
    db: Session = Depends(get_db),
) -> UserDto:
    """Endpoint for getting a user"""
    user_id = request.state.user_id

    user = user_service.get_user(db=db, user_id=user_id)

    return UserDto(
        user_id=str(user.id),
        username=user.username,
        email=user.email,
    )


@router.patch("/users/password")
@auth_required
def change_password(
    request: Request,
    body: ChangePasswordInput,
) -> str:
    """Endpoint for changing a user's password"""
    token = request.state.token

    response = user_service.change_password(
        token=token,
        current_password=body.previous_password,
        new_password=body.proposed_password,
    )

    return "success"
