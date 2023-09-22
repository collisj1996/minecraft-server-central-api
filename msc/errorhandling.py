"""Error handling for msc API"""
import logging
import pprint
import traceback
from json import JSONDecodeError

from exceptiongroup import ExceptionGroup
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from msc.config import config
from msc.dto.util import ErrorOutputDto
from msc.errors import ApplicationError
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
    @app.exception_handler(ApplicationError)
    def handle_application_error(request: Request, exception: ApplicationError):
        logger.exception(
            f"Returning {exception.get_http_status_code()}: {exception.message}",
        )
        return JSONResponse(
            content=exception.to_dto().dict(),
            status_code=exception.get_http_status_code(),
        )

    @app.exception_handler(RequestValidationError)
    def handle_request_validation_error(
        request: Request, exception: RequestValidationError
    ):
        logger.exception(f"Pydantic validation error occurred: {exception}")

        return JSONResponse(
            content=ErrorOutputDto(
                type="validation_error",
                message=str(exception),
                data={"errors": exception.errors()},
            ).dict(),
            status_code=400,
        )

    @app.exception_handler(ValueError)
    def handle_value_error(request: Request, exception: ValueError):
        uuid_error = "value is not a valid uuid"

        if uuid_error in str(exception):
            logger.exception(exception)

            return JSONResponse(
                content=ErrorOutputDto(
                    type="value_error",
                    message=str(exception),
                ).dict(),
                status_code=400,
            )
        elif isinstance(exception, JSONDecodeError):
            logger.exception(f"JSONDecode error occurred: {exception}")

            return JSONResponse(
                content=ErrorOutputDto(
                    type="value_error",
                    message="Invalid JSON",
                ).dict(),
                status_code=400,
            )

        logger.error(f"Unhandled ResponseValidationError occurred: {exception}")

        error_data = _get_exception_error_data(exception)

        return JSONResponse(
            content=ErrorOutputDto(
                message="Error 500",
                data=error_data,
            ).dict(),
            status_code=500,
        )

    @app.exception_handler(ResponseValidationError)
    def handle_response_validation_error(
        request: Request,
        exception: ResponseValidationError,
    ):
        logger.exception(
            f"Response validation error: {_format_pydantic_errors(exception)}"
        )
        exception = _format_pydantic_errors(exception)

        return JSONResponse(
            content=ErrorOutputDto(
                type="error_building_response",
                message=str(exception),
                data={"errors": exception.errors()},
            ).dict(),
            status_code=500,
        )

    @app.exception_handler(Exception)
    def handle_exception(request: Request, exception: Exception):
        if isinstance(exception, ExceptionGroup):
            if len(exception.exceptions) == 1:
                exception = exception.exceptions[0]

        trace = "".join(traceback.format_exception(exception))
        logger.error(f"Unhandled exception occurred: {exception}\n{trace}")
        error_data = _get_exception_error_data(exception)

        return JSONResponse(
            status_code=500,
            content={"message": "An unexpected error occurred", "error": error_data},
        )
