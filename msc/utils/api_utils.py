from functools import wraps

from fastapi import HTTPException, Request

from msc.errors import InternalError, Unauthorized


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request", None)
        if not request:
            raise InternalError("Request object not found")
        if not request.state.authorised:
            raise Unauthorized("Not authorised")
        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request", None)
        if not request:
            raise InternalError("Request object not found")
        if not request.state.is_admin:
            raise Unauthorized("Not authorised")
        return func(*args, **kwargs)

    return wrapper


def get_client_ip(request):
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

    return for_ip
