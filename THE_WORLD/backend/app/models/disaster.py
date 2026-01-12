"""
THE_WORLD - Disaster Model
Database model for disaster events with spatial data
"""

from app.database import db
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import TIMESTAMP


class Disaster(db.Model):
    """Disaster event model with spatial location data"""
    
    __tablename__ = 'disasters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    disaster_type = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    geom = Column(Geometry('POINT', srid=4326), nullable=True)
    occurred_at = Column(TIMESTAMP, nullable=False, index=True)
    magnitude = Column(Numeric(10, 2), nullable=True)
    severity = Column(String(50), nullable=True, index=True)
    status = Column(String(50), nullable=True, index=True)
    source = Column(String(255), nullable=True)
    source_id = Column(String(255), nullable=True)
    url = Column(Text, nullable=True)
    affected_area = Column(Geometry('POLYGON', srid=4326), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    data_fetched_at = Column(TIMESTAMP, nullable=True)
    
    # Unique constraint to prevent duplicates
    __table_args__ = (
        UniqueConstraint('source', 'source_id', name='unique_disaster_source'),
    )
    
    def __init__(self, disaster_type, latitude, longitude, occurred_at, **kwargs):
        """Initialize disaster with coordinates and timestamp"""
        self.disaster_type = disaster_type
        self.latitude = latitude
        self.longitude = longitude
        self.occurred_at = occurred_at
        
        # Create PostGIS geometry from coordinates
        if latitude and longitude:
            self.geom = f'POINT({longitude} {latitude})'
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert disaster to dictionary"""
        return {
            'id': self.id,
            'disaster_type': self.disaster_type,
            'title': self.title,
            'description': self.description,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'occurred_at': self.occurred_at.isoformat() if self.occurred_at else None,
            'magnitude': float(self.magnitude) if self.magnitude else None,
            'severity': self.severity,
            'status': self.status,
            'source': self.source,
            'source_id': self.source_id,
            'url': self.url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'data_fetched_at': self.data_fetched_at.isoformat() if self.data_fetched_at else None
        }
    
    def to_geojson(self):
        """Convert disaster to GeoJSON format"""
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(self.longitude), float(self.latitude)]
            },
            'properties': self.to_dict()
        }
    
    def __repr__(self):
        return f'<Disaster {self.disaster_type} at ({self.latitude}, {self.longitude})>'
