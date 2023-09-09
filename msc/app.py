"""
Contains code to create the FastAPI application and initialise the web server
"""
import logging

from fastapi import FastAPI

from msc.config import config
from . import loggingutil
from .api import server_api

logger = logging.getLogger(__name__)


def create_app():
    """
    Creates the FastAPI application and returns it
    """

    logging.basicConfig(level=logging.INFO)

    app = FastAPI()

    logger.info("MSC Initialising")
    register_routers(app)
    logger.info("MSC Initialised")

    return app


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
