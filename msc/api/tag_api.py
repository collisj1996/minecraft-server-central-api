from fastapi import APIRouter
from fastapi.requests import Request

from msc.dto.tag_dto import (
    GetTagsOutputDto,
)
from msc.constants import ALLOWED_TAGS

router = APIRouter()


@router.get("/tags")
def get_tags(
    request: Request,
):
    """Endpoint for getting maintained tags"""

    return GetTagsOutputDto(__root__=ALLOWED_TAGS)
