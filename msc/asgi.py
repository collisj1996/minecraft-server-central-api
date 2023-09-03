"""
ASGI Entry point for web server
"""

from .app import create_app

application = create_app()