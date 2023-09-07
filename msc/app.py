"""
Contains code to create the FastAPI application and initialise the web server
"""
import logging

from .api import server_api

logger = logging.getLogger(__name__)


def create_app():
    """
    Creates the FastAPI application and returns it

    Returns:
        FastAPI: The FastAPI application
    """
    from fastapi import FastAPI

    app = FastAPI()

    register_routers(app)

    return app


def init_logging():
    level_name = config.logging_level


def register_routers(app):
    app.include_router(server_api.router, tags=["server"])
