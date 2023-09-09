# main.py
from fastapi import APIRouter

from msc.services import server_service

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Hello, World!"}


@router.get("/ping")
def ping():
    return {"message": "pong"}


@router.get("/health")
def health():
    return {"message": "healthy"}


@router.get("/version")
def version():
    return {"version": "0.0.1"}


@router.get("/servers")
def get_servers():

    servers = server_service.get_servers()

    return servers