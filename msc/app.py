"""
Contains code to create the FastAPI application and initialise the web server
"""
import logging

from fastapi import FastAPI
from starlette.requests import Request

from msc import db
from msc.config import config

from . import loggingutil
from .api import migration_api, server_api, util_api, vote_api

logger = logging.getLogger(__name__)


def create_app():
    """
    Creates the FastAPI application and returns it
    """

    logging.basicConfig(level=logging.INFO)

    app = FastAPI()

    logger.info("MSC Initialising")
    init_middleware(app)
    register_routers(app)
    logger.info("MSC Initialised")

    return app


def init_middleware(app):
    logger.info("Intialising middleware")

    @app.middleware("http")
    async def global_request_middleware(request: Request, call_next):

        request.state.authorised = False

        if config.development_mode and "msc-user-id" in request.headers:
            request.state.user_id = request.headers["msc-user-id"]
        elif "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            # if auth_header.startswith("Bearer "):
            #     token = auth_header.split(" ")[1]
            #     request.state.user_id = token

            # Validate the token
            # Decode the token

        logger.info("Request: %s", request)
        response = await call_next(request)
        logger.info("Response: %s", response)

        # End the session
        db.end_session()

        # handle CORS
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"

        return response


def init_logging():
    level_name = config.logging_level
    level = logging._nameToLevel[level_name]

    loggingutil.initialise_logging(
        level=level,
        show_timestamps=config.logging_show_timestamps,
        colour=config.logging_enable_colour,
    )


def register_routers(app):
    logger.info("registering routers")
    app.include_router(server_api.router, tags=["server"])
    app.include_router(migration_api.router, tags=["migration"])
    app.include_router(util_api.router, tags=["util"])
    app.include_router(vote_api.router, tags=["vote"])
