from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.orm import Session

from msc.database import get_db
from msc.dto.user_dto import UserAddInputDto
from msc.services import user_service

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
