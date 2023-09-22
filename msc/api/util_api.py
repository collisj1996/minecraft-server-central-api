from fastapi import APIRouter
from fastapi.requests import Request

router = APIRouter()


@router.get("/health")
def health():
    return {"message": "healthy"}


@router.get("/client_ip")
def client_ip(request: Request):
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

    return {
        "by": by,
        "for": for_ip,
        "host": host,
        "proto": proto,
        "client_ip": for_ip,
    }
