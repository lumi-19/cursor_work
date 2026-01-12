"""
THE_WORLD - Download Routes
API endpoints for downloading data in various formats
"""

from flask import Blueprint, request, make_response
from app.database import db
from app.models import Disaster, AQIMeasurement
from datetime import datetime
import csv
import io
import json
import zipfile

bp = Blueprint('download', __name__)


@bp.route('/disasters', methods=['GET'])
def download_disasters():
    """Download disaster data in specified format"""
    try:
        format_type = request.args.get('format', 'csv').lower()
        
        # Get filtered disasters (reuse disasters route logic)
        from app.routes.disasters import get_disasters
        response = get_disasters()
        data = response.get_json()
        
        if not data.get('success'):
            return response
        
        disasters = data['data']
        
        # Generate file based on format
        if format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            if disasters:
                writer.writerow(disasters[0].keys())
                # Write data
                for disaster in disasters:
                    writer.writerow(disaster.values())
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=disasters_{datetime.now().strftime("%Y%m%d")}.csv'
            return response
        
        elif format_type == 'json':
            response = make_response(json.dumps(disasters, indent=2))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename=disasters_{datetime.now().strftime("%Y%m%d")}.json'
            return response
        
        elif format_type == 'geojson':
            features = []
            for disaster in disasters:
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [disaster['longitude'], disaster['latitude']]
                    },
                    'properties': {k: v for k, v in disaster.items() 
                                 if k not in ['latitude', 'longitude']}
                })
            
            geojson = {
                'type': 'FeatureCollection',
                'features': features,
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'source': 'THE_WORLD API'
                }
            }
            
            response = make_response(json.dumps(geojson, indent=2))
            response.headers['Content-Type'] = 'application/geo+json'
            response.headers['Content-Disposition'] = f'attachment; filename=disasters_{datetime.now().strftime("%Y%m%d")}.geojson'
            return response
        
        else:
            return {'error': 'Unsupported format. Use: csv, json, or geojson'}, 400
    
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500


@bp.route('/aqi', methods=['GET'])
def download_aqi():
    """Download AQI data in specified format"""
    try:
        format_type = request.args.get('format', 'csv').lower()
        
        # Get filtered AQI data (reuse aqi route logic)
        from app.routes.aqi import get_aqi
        response = get_aqi()
        data = response.get_json()
        
        if not data.get('success'):
            return response
        
        measurements = data['data']
        
        # Generate file based on format (same logic as disasters)
        if format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            if measurements:
                writer.writerow(measurements[0].keys())
                for measurement in measurements:
                    writer.writerow(measurement.values())
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=aqi_{datetime.now().strftime("%Y%m%d")}.csv'
            return response
        
        elif format_type == 'json':
            response = make_response(json.dumps(measurements, indent=2))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename=aqi_{datetime.now().strftime("%Y%m%d")}.json'
            return response
        
        elif format_type == 'geojson':
            features = []
            for measurement in measurements:
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [measurement['longitude'], measurement['latitude']]
                    },
                    'properties': {k: v for k, v in measurement.items() 
                                 if k not in ['latitude', 'longitude']}
                })
            
            geojson = {
                'type': 'FeatureCollection',
                'features': features,
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'source': 'THE_WORLD API'
                }
            }
            
            response = make_response(json.dumps(geojson, indent=2))
            response.headers['Content-Type'] = 'application/geo+json'
            response.headers['Content-Disposition'] = f'attachment; filename=aqi_{datetime.now().strftime("%Y%m%d")}.geojson'
            return response
        
        else:
            return {'error': 'Unsupported format'}, 400
    
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
