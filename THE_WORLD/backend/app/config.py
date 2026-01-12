"""
THE_WORLD - Configuration Module
Centralized configuration management
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_RUN_PORT = int(os.getenv('FLASK_RUN_PORT', 5000))
    FLASK_RUN_HOST = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    
    # Database Configuration (PostGIS)
    POSTGIS_USER = os.getenv('POSTGIS_USER', 'postgres')
    POSTGIS_PASSWORD = os.getenv('POSTGIS_PASSWORD', '')
    POSTGIS_DB = os.getenv('POSTGIS_DB', 'WebGis')
    POSTGIS_HOST = os.getenv('POSTGIS_HOST', 'localhost')
    POSTGIS_PORT = os.getenv('POSTGIS_PORT', '5432')
    
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGIS_USER}:{POSTGIS_PASSWORD}"
        f"@{POSTGIS_HOST}:{POSTGIS_PORT}/{POSTGIS_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': False
    }
    
    # GeoServer Configuration
    GEOSERVER_URL = os.getenv('GEOSERVER_URL', 'http://localhost:8080/geoserver')
    GEOSERVER_ADMIN_USER = os.getenv('GEOSERVER_ADMIN_USER', 'admin')
    GEOSERVER_ADMIN_PASSWORD = os.getenv('GEOSERVER_ADMIN_PASSWORD', 'geoserver')
    GEOSERVER_WORKSPACE = os.getenv('GEOSERVER_WORKSPACE', 'WebGis')
    GEOSERVER_STORE = os.getenv('GEOSERVER_STORE', 'WebGis_postgis')
    
    # External API Keys
    OPENAQ_API_KEY = os.getenv('OPENAQ_API_KEY', '')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # API Configuration
    DISASTER_UPDATE_INTERVAL = 600  # 10 minutes in seconds
    AQI_UPDATE_INTERVAL = 900  # 15 minutes in seconds


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
