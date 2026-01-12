"""
THE_WORLD - City Routes
API endpoints for city data
"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models import City
from sqlalchemy import or_

bp = Blueprint('cities', __name__)


@bp.route('', methods=['GET'])
def get_cities():
    """Get list of cities with optional filtering"""
    try:
        country = request.args.get('country')
        country_code = request.args.get('country_code')
        search = request.args.get('search')
        limit = min(request.args.get('limit', 100, type=int), 1000)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = City.query
        
        # Apply filters
        if country:
            query = query.filter(City.country.ilike(f'%{country}%'))
        
        if country_code:
            query = query.filter(City.country_code == country_code.upper())
        
        if search:
            query = query.filter(
                or_(
                    City.name.ilike(f'%{search}%'),
                    City.country.ilike(f'%{search}%')
                )
            )
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        cities = query.limit(limit).offset(offset).all()
        
        # Serialize results
        data = [city.to_dict() for city in cities]
        
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


@bp.route('/<int:city_id>', methods=['GET'])
def get_city(city_id):
    """Get a specific city by ID"""
    try:
        city = City.query.get_or_404(city_id)
        return jsonify({
            'success': True,
            'data': city.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
