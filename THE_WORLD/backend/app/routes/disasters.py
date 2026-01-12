"""
THE_WORLD - Disaster Routes
API endpoints for disaster data
"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Disaster
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import json

from app.services.disaster_api import disaster_api_service

bp = Blueprint('disasters', __name__)


@bp.route('/fetch', methods=['POST'])
def fetch_disasters():
    """Trigger manual fetch of disaster data"""
    try:
        days = request.args.get('days', 7, type=int)
        
        # Fetch data
        disasters_data = disaster_api_service.fetch_all_disasters(days=days)
        
        # Save to database
        result = disaster_api_service.save_disasters_to_db(disasters_data)
        
        return jsonify({
            'success': True,
            'message': 'Disaster data fetch completed',
            'details': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('', methods=['GET'])
def get_disasters():
    """Get disaster events with optional filtering"""
    try:
        # Parse query parameters
        disaster_type = request.args.get('disaster_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        min_magnitude = request.args.get('min_magnitude', type=float)
        max_magnitude = request.args.get('max_magnitude', type=float)
        bbox = request.args.get('bbox')  # min_lon,min_lat,max_lon,max_lat
        limit = min(request.args.get('limit', 100, type=int), 1000)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = Disaster.query
        
        # Apply filters
        if disaster_type:
            query = query.filter(Disaster.disaster_type == disaster_type)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Disaster.occurred_at >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid date format', 'message': 'Date must be in ISO 8601 format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Disaster.occurred_at <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid date format', 'message': 'Date must be in ISO 8601 format'}), 400
        
        if min_magnitude is not None:
            query = query.filter(Disaster.magnitude >= min_magnitude)
        
        if max_magnitude is not None:
            query = query.filter(Disaster.magnitude <= max_magnitude)
        
        if bbox:
            try:
                coords = [float(x) for x in bbox.split(',')]
                if len(coords) == 4:
                    min_lon, min_lat, max_lon, max_lat = coords
                    query = query.filter(
                        and_(
                            Disaster.longitude >= min_lon,
                            Disaster.longitude <= max_lon,
                            Disaster.latitude >= min_lat,
                            Disaster.latitude <= max_lat
                        )
                    )
            except (ValueError, IndexError):
                return jsonify({'error': 'Invalid bbox format', 'message': 'Bbox must be: min_lon,min_lat,max_lon,max_lat'}), 400
        
        # Order by occurred_at (most recent first)
        query = query.order_by(Disaster.occurred_at.desc())
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        disasters = query.limit(limit).offset(offset).all()
        
        # Serialize results
        data = [disaster.to_dict() for disaster in disasters]
        
        return jsonify({
            'success': True,
            'count': len(data),
            'total': total_count,
            'offset': offset,
            'limit': limit,
            'data': data
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:disaster_id>', methods=['GET'])
def get_disaster(disaster_id):
    """Get a specific disaster event by ID"""
    try:
        disaster = Disaster.query.get_or_404(disaster_id)
        return jsonify({
            'success': True,
            'data': disaster.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/geojson', methods=['GET'])
def get_disasters_geojson():
    """Get disaster events as GeoJSON"""
    try:
        # Reuse get_disasters logic
        response = get_disasters()
        data = response.get_json()
        
        if not data.get('success'):
            return response
        
        # Convert to GeoJSON format
        features = []
        for disaster_data in data['data']:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [disaster_data['longitude'], disaster_data['latitude']]
                },
                'properties': {k: v for k, v in disaster_data.items() 
                             if k not in ['latitude', 'longitude']}
            })
        
        return jsonify({
            'type': 'FeatureCollection',
            'features': features
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/types', methods=['GET'])
def get_disaster_types():
    """Get list of available disaster types"""
    try:
        types = db.session.query(Disaster.disaster_type).distinct().all()
        disaster_types = [t[0] for t in types if t[0]]
        
        return jsonify({
            'success': True,
            'data': disaster_types
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
