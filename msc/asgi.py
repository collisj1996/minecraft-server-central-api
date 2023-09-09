"""
ASGI Entry point for web server
"""
import logging

logger = logging.getLogger(__name__)

from .app import create_app

logger.info("Creating FastAPI application")

application = create_app()
