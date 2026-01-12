"""
THE_WORLD - AQI Routes
API endpoints for Air Quality Index data
"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models import AQIMeasurement
from sqlalchemy import and_, desc
from datetime import datetime
import json

from app.services.aqi_api import aqi_service

bp = Blueprint('aqi', __name__)


@bp.route('/fetch', methods=['POST'])
def fetch_aqi():
    """Trigger manual fetch of AQI data"""
    try:
        cities = request.json.get('cities') if request.is_json else None
        limit = request.args.get('limit', 50, type=int)
        
        # Fetch data
        aqi_data = aqi_service.fetch_all_aqi(cities=cities, limit=limit)
        
        # Save to database
        result = aqi_service.save_measurements_to_db(aqi_data)
        
        return jsonify({
            'success': True,
            'message': 'AQI data fetch completed',
            'details': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('', methods=['GET'])
def get_aqi():
    """Get AQI measurements with optional filtering"""
    try:
        # Parse query parameters
        city_id = request.args.get('city_id', type=int)
        city_name = request.args.get('city_name')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        min_aqi = request.args.get('min_aqi', type=int)
        max_aqi = request.args.get('max_aqi', type=int)
        bbox = request.args.get('bbox')
        limit = min(request.args.get('limit', 100, type=int), 1000)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = AQIMeasurement.query
        
        # Apply filters
        if city_id:
            query = query.filter(AQIMeasurement.city_id == city_id)
        
        if city_name:
            query = query.filter(AQIMeasurement.city_name.ilike(f'%{city_name}%'))
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(AQIMeasurement.measured_at >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(AQIMeasurement.measured_at <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        
        if min_aqi is not None:
            query = query.filter(AQIMeasurement.aqi_value >= min_aqi)
        
        if max_aqi is not None:
            query = query.filter(AQIMeasurement.aqi_value <= max_aqi)
        
        if bbox:
            try:
                coords = [float(x) for x in bbox.split(',')]
                if len(coords) == 4:
                    min_lon, min_lat, max_lon, max_lat = coords
                    query = query.filter(
                        and_(
                            AQIMeasurement.longitude >= min_lon,
                            AQIMeasurement.longitude <= max_lon,
                            AQIMeasurement.latitude >= min_lat,
                            AQIMeasurement.latitude <= max_lat
                        )
                    )
            except (ValueError, IndexError):
                return jsonify({'error': 'Invalid bbox format'}), 400
        
        # Order by measured_at (most recent first)
        query = query.order_by(desc(AQIMeasurement.measured_at))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        measurements = query.limit(limit).offset(offset).all()
        
        # Serialize results
        data = [measurement.to_dict() for measurement in measurements]
        
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


@bp.route('/latest', methods=['GET'])
def get_latest_aqi():
    """Get latest AQI measurements for all cities or specific cities"""
    try:
        city_ids = request.args.get('city_ids')  # Comma-separated
        city_names = request.args.get('city_names')  # Comma-separated
        
        query = AQIMeasurement.query
        
        if city_ids:
            ids = [int(x.strip()) for x in city_ids.split(',')]
            query = query.filter(AQIMeasurement.city_id.in_(ids))
        
        if city_names:
            names = [name.strip() for name in city_names.split(',')]
            query = query.filter(AQIMeasurement.city_name.in_(names))
        
        # Get latest for each city
        # This is a simplified approach - for production, use window functions
        measurements = query.order_by(
            desc(AQIMeasurement.city_name),
            desc(AQIMeasurement.measured_at)
        ).all()
        
        # Deduplicate by city (keep most recent)
        seen_cities = set()
        unique_measurements = []
        for measurement in measurements:
            city_key = measurement.city_id or measurement.city_name
            if city_key not in seen_cities:
                seen_cities.add(city_key)
                unique_measurements.append(measurement)
        
        data = [m.to_dict() for m in unique_measurements]
        
        return jsonify({
            'success': True,
            'count': len(data),
            'data': data
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/geojson', methods=['GET'])
def get_aqi_geojson():
    """Get AQI measurements as GeoJSON"""
    try:
        # Reuse get_aqi logic
        response = get_aqi()
        data = response.get_json()
        
        if not data.get('success'):
            return response
        
        # Convert to GeoJSON format
        features = []
        for aqi_data in data['data']:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [aqi_data['longitude'], aqi_data['latitude']]
                },
                'properties': {k: v for k, v in aqi_data.items() 
                             if k not in ['latitude', 'longitude']}
            })
        
        return jsonify({
            'type': 'FeatureCollection',
            'features': features
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
