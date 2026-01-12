"""
THE_WORLD - City Model
Database model for cities with spatial data
"""

from app.database import db
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import TIMESTAMP


class City(db.Model):
    """City model with spatial location data"""
    
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    country_code = Column(String(2), index=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    geom = Column(Geometry('POINT', srid=4326), nullable=True)
    boundary = Column(Geometry('POLYGON', srid=4326), nullable=True)
    population = Column(Integer, nullable=True)
    timezone = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    aqi_measurements = db.relationship('AQIMeasurement', backref='city', lazy='dynamic')
    
    def __init__(self, name, country, latitude, longitude, **kwargs):
        """Initialize city with coordinates"""
        self.name = name
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        
        # Create PostGIS geometry from coordinates
        if latitude and longitude:
            self.geom = f'POINT({longitude} {latitude})'
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert city to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'country_code': self.country_code,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'population': self.population,
            'timezone': self.timezone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_geojson(self):
        """Convert city to GeoJSON format"""
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(self.longitude), float(self.latitude)]
            },
            'properties': self.to_dict()
        }
    
    def __repr__(self):
        return f'<City {self.name}, {self.country}>'
