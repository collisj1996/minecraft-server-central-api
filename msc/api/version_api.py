from fastapi import APIRouter, Depends
from fastapi.requests import Request

from msc.dto.version_dto import (
    GetVersionsOutputDto,
)
from sqlalchemy.orm import Session
from msc.database import get_db

from msc.services.version_service import get_versions

router = APIRouter()


@router.get("/versions")
def get_minecraft_versions(
    request: Request,
    db: Session = Depends(get_db),
):
    """Endpoint for getting maintained minecraft versions"""

    versions = get_versions(db=db)

    return GetVersionsOutputDto.from_service(
        versions=versions,
    )
