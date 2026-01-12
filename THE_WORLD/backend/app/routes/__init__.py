"""
THE_WORLD - Routes Package
Import all route blueprints
"""

# Import routes here to make them available
from app.routes import disasters
from app.routes import aqi
from app.routes import cities
from app.routes import comparison
from app.routes import correlation
from app.routes import download
from app.routes import chatbot

__all__ = ['disasters', 'aqi', 'cities', 'comparison', 'correlation', 'download', 'chatbot']
