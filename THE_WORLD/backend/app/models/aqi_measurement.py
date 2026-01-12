"""
THE_WORLD - AQI Measurement Model
Database model for Air Quality Index measurements with spatial data
"""

from app.database import db
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import TIMESTAMP


class AQIMeasurement(db.Model):
    """AQI measurement model with spatial location and pollutant data"""
    
    __tablename__ = 'aqi_measurements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='SET NULL'), nullable=True, index=True)
    city_name = Column(String(255), nullable=True, index=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    geom = Column(Geometry('POINT', srid=4326), nullable=True)
    measured_at = Column(TIMESTAMP, nullable=False, index=True)
    aqi_value = Column(Integer, nullable=True, index=True)
    aqi_category = Column(String(50), nullable=True)
    pm25 = Column(Numeric(8, 2), nullable=True)
    pm10 = Column(Numeric(8, 2), nullable=True)
    o3 = Column(Numeric(8, 2), nullable=True)
    no2 = Column(Numeric(8, 2), nullable=True)
    co = Column(Numeric(8, 2), nullable=True)
    so2 = Column(Numeric(8, 2), nullable=True)
    source = Column(String(255), nullable=True)
    source_id = Column(String(255), nullable=True)
    url = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    data_fetched_at = Column(TIMESTAMP, nullable=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_aqi_city_time', 'city_id', 'measured_at'),
        Index('idx_aqi_city_date', 'city_id', 'measured_at'),
    )
    
    def __init__(self, latitude, longitude, measured_at, **kwargs):
        """Initialize AQI measurement with coordinates and timestamp"""
        self.latitude = latitude
        self.longitude = longitude
        self.measured_at = measured_at
        
        # Create PostGIS geometry from coordinates
        if latitude and longitude:
            self.geom = f'POINT({longitude} {latitude})'
        
        # Calculate AQI category if aqi_value is provided
        if 'aqi_value' in kwargs and kwargs['aqi_value']:
            self.aqi_value = kwargs['aqi_value']
            self.aqi_category = self._calculate_aqi_category(kwargs['aqi_value'])
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'aqi_value':
                setattr(self, key, value)
    
    @staticmethod
    def _calculate_aqi_category(aqi_value):
        """Calculate AQI category from AQI value"""
        if aqi_value <= 50:
            return 'good'
        elif aqi_value <= 100:
            return 'moderate'
        elif aqi_value <= 150:
            return 'unhealthy_for_sensitive_groups'
        elif aqi_value <= 200:
            return 'unhealthy'
        elif aqi_value <= 300:
            return 'very_unhealthy'
        else:
            return 'hazardous'
    
    def calculate_aqi_from_pollutants(self):
        """Calculate overall AQI from individual pollutants (simplified)"""
        # This is a simplified calculation - real AQI calculation is more complex
        # Typically uses the maximum of individual pollutant AQIs
        if self.pm25:
            # Simplified PM2.5 to AQI conversion
            return min(500, int((self.pm25 / 12.0) * 50))
        return None
    
    def to_dict(self):
        """Convert AQI measurement to dictionary"""
        return {
            'id': self.id,
            'city_id': self.city_id,
            'city_name': self.city_name,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'measured_at': self.measured_at.isoformat() if self.measured_at else None,
            'aqi_value': self.aqi_value,
            'aqi_category': self.aqi_category,
            'pm25': float(self.pm25) if self.pm25 else None,
            'pm10': float(self.pm10) if self.pm10 else None,
            'o3': float(self.o3) if self.o3 else None,
            'no2': float(self.no2) if self.no2 else None,
            'co': float(self.co) if self.co else None,
            'so2': float(self.so2) if self.so2 else None,
            'source': self.source,
            'url': self.url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_geojson(self):
        """Convert AQI measurement to GeoJSON format"""
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(self.longitude), float(self.latitude)]
            },
            'properties': self.to_dict()
        }
    
    def __repr__(self):
        return f'<AQIMeasurement {self.city_name} AQI: {self.aqi_value} at {self.measured_at}>'
