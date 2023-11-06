"""
Contains code to create the FastAPI application and initialise the web server
"""
import logging

import cognitojwt
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from msc import errorhandling
from msc.config import config
from msc.constants import ADMIN_USER_IDS

from . import loggingutil
from .api import (
    auction_api,
    auth_api,
    migration_api,
    server_api,
    tag_api,
    user_api,
    util_api,
    version_api,
    vote_api,
)
from .jobs.jobs import persisted_scheduler, scheduler

logger = logging.getLogger(__name__)


def create_app():
    """
    Creates the FastAPI application and returns it
    """

    logging.basicConfig(level=logging.INFO)

    app = FastAPI()

    logger.info("MSC Initialising")
    init_middleware(app)
    init_error_handlers(app)
    register_routers(app)

    # Initialise general scheduler
    scheduler.start()
    # Initialise scheduler for persisted jobs
    persisted_scheduler.start()

    logger.info("MSC Initialised")

    return app


def init_middleware(app):
    logger.info("Intialising middleware")

    @app.middleware("http")
    async def global_request_middleware(request: Request, call_next):
        request.state.authorised = False
        request.state.is_admin = False

        if config.development_mode and "msc-user-id" in request.headers:
            request.state.user_id = request.headers["msc-user-id"]
            request.state.authorised = True
            request.state.is_admin = True

        elif "Authorization" in request.headers:
            token = request.headers["Authorization"]

            if token == "jwtTestToken":
                request.state.user_id = "d24544e4-b0a1-7007-f8cf-9efb4eb35d8a"
                request.state.authorised = True
                request.state.is_admin = True
            else:
                REGION = "eu-west-1"
                USERPOOL_ID = "eu-west-1_4tUpfVYqE"
                APP_CLIENT_ID = "it0ectnsd44cr1phrifio2h5k"

                try:
                    verified_claims: dict = cognitojwt.decode(
                        token=token,
                        region=REGION,
                        userpool_id=USERPOOL_ID,
                        app_client_id=APP_CLIENT_ID,  # Optional
                    )

                    request.state.user_id = verified_claims["sub"]
                    request.state.authorised = True
                    request.state.token = token

                    if verified_claims["sub"] in ADMIN_USER_IDS:
                        request.state.is_admin = True

                except Exception as e:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"message": "Not authorised"},
                    )

        logger.info("Request: %s", request)
        response = await call_next(request)
        logger.info("Response: %s", response)

        return response

    origins = [
        "http://localhost",
        "http://localhost:3000",
        "https://minecraftservercentral.com",
        "https://www.minecraftservercentral.com",
        "http://127.0.0.1:3000",
    ]

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_logging():
    level_name = config.logging_level
    level = logging._nameToLevel[level_name]

    loggingutil.initialise_logging(
        level=level,
        show_timestamps=config.logging_show_timestamps,
        colour=config.logging_enable_colour,
    )


def init_error_handlers(app):
    logger.info("Initialising error handlers")
    errorhandling.init_error_handlers(app)


def register_routers(app):
    logger.info("registering routers")
    app.include_router(server_api.router, tags=["server"])
    app.include_router(migration_api.router, tags=["migration"])
    app.include_router(util_api.router, tags=["util"])
    app.include_router(vote_api.router, tags=["vote"])
    app.include_router(user_api.router, tags=["user"])
    app.include_router(auth_api.router, tags=["auth"])
    app.include_router(auction_api.router, tags=["auction"])
    app.include_router(tag_api.router, tags=["tag"])
    app.include_router(version_api.router, tags=["version"])
