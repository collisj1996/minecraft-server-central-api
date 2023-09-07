# main.py
from fastapi import APIRouter

router = APIRouter()

router.get("/")


def read_root():
    return {"message": "Hello, World!"}


router.get("/ping")


def ping():
    return {"message": "pong"}


router.get("/health")


def health():
    return {"message": "healthy"}


router.get("/version")


def version():
    return {"version": "0.0.1"}
