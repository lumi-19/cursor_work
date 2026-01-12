"""
THE_WORLD - Comparison Routes
API endpoints for comparing AQI data between cities
"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models import AQIMeasurement
from sqlalchemy import func, desc
from datetime import datetime

bp = Blueprint('comparison', __name__)


@bp.route('/aqi', methods=['GET'])
def compare_aqi():
    """Compare AQI data between multiple cities"""
    try:
        city_ids = request.args.get('city_ids')  # Required, comma-separated
        date = request.args.get('date')  # Optional, defaults to latest
        
        if not city_ids:
            return jsonify({'error': 'city_ids parameter is required'}), 400
        
        # Parse city IDs
        ids = [int(x.strip()) for x in city_ids.split(',')]
        
        # Build query
        query = AQIMeasurement.query.filter(AQIMeasurement.city_id.in_(ids))
        
        # Apply date filter if provided
        if date:
            try:
                target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                query = query.filter(func.date(AQIMeasurement.measured_at) == func.date(target_date))
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        
        # Get measurements (ordered by city and time)
        measurements = query.order_by(
            AQIMeasurement.city_id,
            desc(AQIMeasurement.measured_at)
        ).all()
        
        # Group by city and get most recent for each
        city_data = {}
        for measurement in measurements:
            city_id = measurement.city_id
            if city_id not in city_data:
                city_data[city_id] = measurement
        
        # Build response
        cities_list = []
        aqi_values = []
        
        for city_id, measurement in city_data.items():
            city_info = measurement.to_dict()
            cities_list.append(city_info)
            if measurement.aqi_value:
                aqi_values.append(measurement.aqi_value)
        
        # Calculate statistics
        statistics = {}
        if aqi_values:
            statistics = {
                'highest_aqi': max(aqi_values),
                'lowest_aqi': min(aqi_values),
                'average_aqi': round(sum(aqi_values) / len(aqi_values), 2)
            }
        
        comparison_date = date or (cities_list[0]['measured_at'] if cities_list else None)
        
        return jsonify({
            'success': True,
            'comparison_date': comparison_date,
            'cities': cities_list,
            'statistics': statistics
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
