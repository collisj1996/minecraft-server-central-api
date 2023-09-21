"""Error handling for msc API"""
import logging
import pprint
import traceback
from json import JSONDecodeError

from fastapi.exceptions import RequestValidationError, ResponseValidationError
from msc.config import config
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse


logger = logging.getLogger(__name__)

def _format_pydantic_errors(exception: ValidationError):
    return pprint.pformat(exception.errors())


def _get_exception_error_data(exception: Exception):
    error_data = {}
    if str(exception):
        error_data["exception"] = str(exception)
    else:
        error_data["exception"] = str(type(exception).__name__)
    return error_data


def init_error_handlers(app):
    @app.exception_handler(RequestValidationError)
    def handle_request_validation_error(request: Request, exception: RequestValidationError):
        logger.info(f"Request validation error occurred: {exception}")
        error_data = _get_exception_error_data(exception)

        return JSONResponse(
            status_code=400,
            content={
                "message": "Request validation error",
                "error": error_data
            }
        )
    
    @app.exception_handler(ResponseValidationError)
    def handle_response_validation_error(request: Request, exception: ResponseValidationError):
        logger.info(f"Response validation error occurred: {_format_pydantic_errors(exception)}")
        error_data = _get_exception_error_data(exception)

        return JSONResponse(
            status_code=500,
            content={
                "message": "Response validation error",
                "error": error_data
            }
        )

    @app.exception_handler(ValueError)
    def handle_value_error(request: Request, exception: ValueError):

        trace = "".join(traceback.format_exception(exception))
        logger.error(f"Unhandled ValueError occurred: {exception}\n{trace}")
        error_data = _get_exception_error_data(exception)

        return JSONResponse(
            status_code=500,
            content={
                "message": "An unexpected error occurred",
                "error": error_data
            }
        )
        


    @app.exception_handler(Exception)
    def handle_exception(request: Request, exception: Exception):

        trace = "".join(traceback.format_exception(exception))
        logger.error(f"Unhandled exception occurred: {exception}\n{trace}")
        error_data = _get_exception_error_data(exception)

        return JSONResponse(
            status_code=500,
            content={
                "message": "An unexpected error occurred",
                "error": error_data
            }
        )