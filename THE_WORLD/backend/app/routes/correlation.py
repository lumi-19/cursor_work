"""
THE_WORLD - Correlation Routes
API endpoints for disaster-pollution correlation analysis
"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Disaster, AQIMeasurement, City
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from geoalchemy2.functions import ST_Distance

bp = Blueprint('correlation', __name__)


@bp.route('/disaster-aqi', methods=['GET'])
def disaster_aqi_correlation():
    """Analyze correlation between disaster events and AQI data"""
    try:
        disaster_id = request.args.get('disaster_id', type=int)
        city_id = request.args.get('city_id', type=int)
        disaster_type = request.args.get('disaster_type')
        pre_days = request.args.get('pre_days', 7, type=int)
        post_days = request.args.get('post_days', 30, type=int)
        distance_km = request.args.get('distance_km', 100, type=float)
        
        # Build disaster query
        disaster_query = Disaster.query
        
        if disaster_id:
            disaster_query = disaster_query.filter(Disaster.id == disaster_id)
        
        if disaster_type:
            disaster_query = disaster_query.filter(Disaster.disaster_type == disaster_type)
        
        disasters = disaster_query.all()
        
        if not disasters:
            return jsonify({
                'success': True,
                'correlations': [],
                'message': 'No disasters found matching criteria'
            })
        
        correlations = []
        
        for disaster in disasters:
            # Calculate time windows
            disaster_date = disaster.occurred_at
            pre_start = disaster_date - timedelta(days=pre_days)
            pre_end = disaster_date
            post_start = disaster_date
            post_end = disaster_date + timedelta(days=post_days)
            
            # Find cities within distance
            # Using a simplified bounding box approach for distance filtering
            # For production, use PostGIS ST_DWithin for accurate distance calculations
            
            # Query AQI measurements in the area and time range
            aqi_query = AQIMeasurement.query.filter(
                and_(
                    # Bounding box approximation (simplified)
                    AQIMeasurement.latitude >= disaster.latitude - (distance_km / 111.0),
                    AQIMeasurement.latitude <= disaster.latitude + (distance_km / 111.0),
                    AQIMeasurement.longitude >= disaster.longitude - (distance_km / (111.0 * abs(disaster.latitude / 90.0))),
                    AQIMeasurement.longitude <= disaster.longitude + (distance_km / (111.0 * abs(disaster.latitude / 90.0)))
                )
            )
            
            # Pre-disaster AQI
            pre_aqi = aqi_query.filter(
                and_(
                    AQIMeasurement.measured_at >= pre_start,
                    AQIMeasurement.measured_at < pre_end
                )
            ).all()
            
            # Post-disaster AQI
            post_aqi = aqi_query.filter(
                and_(
                    AQIMeasurement.measured_at >= post_start,
                    AQIMeasurement.measured_at <= post_end
                )
            ).all()
            
            # Calculate statistics per city
            affected_cities = {}
            
            # Process pre-disaster data
            for measurement in pre_aqi:
                city_key = measurement.city_id or measurement.city_name
                if city_key not in affected_cities:
                    affected_cities[city_key] = {
                        'city_id': measurement.city_id,
                        'city_name': measurement.city_name,
                        'pre_aqi_values': [],
                        'post_aqi_values': []
                    }
                if measurement.aqi_value:
                    affected_cities[city_key]['pre_aqi_values'].append(measurement.aqi_value)
            
            # Process post-disaster data
            for measurement in post_aqi:
                city_key = measurement.city_id or measurement.city_name
                if city_key not in affected_cities:
                    affected_cities[city_key] = {
                        'city_id': measurement.city_id,
                        'city_name': measurement.city_name,
                        'pre_aqi_values': [],
                        'post_aqi_values': []
                    }
                if measurement.aqi_value:
                    affected_cities[city_key]['post_aqi_values'].append(measurement.aqi_value)
            
            # Calculate correlation metrics for each city
            cities_affected = []
            for city_key, city_data in affected_cities.items():
                if not city_data['post_aqi_values']:
                    continue
                
                pre_avg = sum(city_data['pre_aqi_values']) / len(city_data['pre_aqi_values']) if city_data['pre_aqi_values'] else None
                post_avg = sum(city_data['post_aqi_values']) / len(city_data['post_aqi_values'])
                peak_aqi = max(city_data['post_aqi_values'])
                
                aqi_change = None
                if pre_avg:
                    aqi_change = ((post_avg - pre_avg) / pre_avg) * 100
                
                cities_affected.append({
                    'city_id': city_data['city_id'],
                    'city_name': city_data['city_name'],
                    'pre_disaster_avg_aqi': round(pre_avg, 2) if pre_avg else None,
                    'post_disaster_avg_aqi': round(post_avg, 2),
                    'aqi_change_percent': round(aqi_change, 2) if aqi_change else None,
                    'peak_aqi': int(peak_aqi),
                    'peak_aqi_date': None  # Would need to track this separately
                })
            
            # Calculate summary statistics
            if cities_affected:
                avg_changes = [c['aqi_change_percent'] for c in cities_affected if c['aqi_change_percent']]
                max_changes = [c['aqi_change_percent'] for c in cities_affected if c['aqi_change_percent']]
                
                summary = {
                    'total_affected_cities': len(cities_affected),
                    'avg_aqi_increase': round(sum(avg_changes) / len(avg_changes), 2) if avg_changes else None,
                    'max_aqi_increase': round(max(max_changes), 2) if max_changes else None
                }
            else:
                summary = {
                    'total_affected_cities': 0,
                    'avg_aqi_increase': None,
                    'max_aqi_increase': None
                }
            
            correlations.append({
                'disaster_id': disaster.id,
                'disaster_type': disaster.disaster_type,
                'disaster_title': disaster.title,
                'disaster_date': disaster.occurred_at.isoformat() if disaster.occurred_at else None,
                'location': {
                    'latitude': float(disaster.latitude),
                    'longitude': float(disaster.longitude)
                },
                'affected_cities': cities_affected,
                'summary': summary
            })
        
        return jsonify({
            'success': True,
            'correlations': correlations
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
