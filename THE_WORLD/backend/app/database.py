"""
THE_WORLD - Database Module
SQLAlchemy database initialization and session management
"""

from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry

db = SQLAlchemy()


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Import all models here to ensure they're registered
        from app.models import City, Disaster, AQIMeasurement
        
        # Create all tables
        db.create_all()
        
        # Create PostGIS extension if it doesn't exist
        try:
            db.session.execute(db.text("CREATE EXTENSION IF NOT EXISTS postgis"))
            db.session.commit()
        except Exception as e:
            print(f"Note: PostGIS extension may already exist or require manual setup: {e}")
            db.session.rollback()
