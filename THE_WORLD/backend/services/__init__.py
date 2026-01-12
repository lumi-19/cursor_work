"""
THE_WORLD - Services Package
External API service integrations
"""

try:
    from app.services.disaster_api import disaster_api_service
    from app.services.aqi_api import aqi_service
except ImportError:
    from services.disaster_api import disaster_api_service
    from services.aqi_api import aqi_service

__all__ = ['disaster_api_service', 'aqi_service']
