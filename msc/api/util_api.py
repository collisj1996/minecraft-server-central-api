from fastapi import APIRouter
from fastapi.requests import Request

router = APIRouter()


@router.get("/health")
def health():
    return {"message": "healthy"}
