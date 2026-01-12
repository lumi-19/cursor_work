"""
THE_WORLD - Helper Utilities
Common utility functions
"""

from datetime import datetime
from functools import wraps
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def handle_api_errors(f):
    """Decorator to handle API errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {f.__name__}: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Internal Server Error',
                'message': str(e)
            }), 500
    return decorated_function


def validate_date(date_string, format='%Y-%m-%dT%H:%M:%S'):
    """Validate and parse date string"""
    try:
        if 'T' in date_string:
            if date_string.endswith('Z'):
                date_string = date_string.replace('Z', '+00:00')
            return datetime.fromisoformat(date_string)
        else:
            return datetime.strptime(date_string, format)
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid date format: {date_string}")


def parse_bbox(bbox_string):
    """Parse bounding box string to coordinates"""
    try:
        coords = [float(x) for x in bbox_string.split(',')]
        if len(coords) != 4:
            raise ValueError("Bounding box must have 4 coordinates")
        return {
            'min_lon': coords[0],
            'min_lat': coords[1],
            'max_lon': coords[2],
            'max_lat': coords[3]
        }
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid bounding box format: {bbox_string}. Expected: min_lon,min_lat,max_lon,max_lat")


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates (Haversine formula)"""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth radius in kilometers
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    
    a = sin(d_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(d_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c  # Distance in kilometers
