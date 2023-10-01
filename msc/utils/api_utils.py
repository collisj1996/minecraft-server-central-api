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
