"""
THE_WORLD - AQI API Service
Fetch AQI data from multiple external APIs
"""

import requests
from datetime import datetime
from app.database import db
from app.models import AQIMeasurement, City
from app.config import Config
import logging

logger = logging.getLogger(__name__)


class AQIService:
    """Service for fetching AQI data from multiple sources"""
    
    def __init__(self):
        self.openaq_base_url = "https://api.openaq.org/v2"
        self.openweather_base_url = "https://api.openweathermap.org/data/2.5"
    
    def fetch_all_aqi(self, cities=None, limit=50):
        """Fetch AQI data from all available sources"""
        all_measurements = []
        
        # Fetch from OpenAQ
        try:
            openaq_measurements = self._fetch_openaq_data(limit=limit)
            all_measurements.extend(openaq_measurements)
        except Exception as e:
            logger.error(f"Error fetching OpenAQ data: {e}")
        
        # Fetch from OpenWeather
        try:
            openweather_measurements = self._fetch_openweather_data(cities=cities)
            all_measurements.extend(openweather_measurements)
        except Exception as e:
            logger.error(f"Error fetching OpenWeather data: {e}")
        
        return all_measurements
    
    def _fetch_openaq_data(self, limit=50):
        """Fetch AQI data from OpenAQ API"""
        measurements = []
        
        try:
            url = f"{self.openaq_base_url}/latest"
            headers = {
                'X-API-Key': Config.OPENAQ_API_KEY if Config.OPENAQ_API_KEY else None
            }
            
            params = {
                'limit': limit,
                'page': 1
            }
            
            # Remove None headers
            headers = {k: v for k, v in headers.items() if v is not None}
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data:
                for result in data['results']:
                    location = result.get('location', {})
                    coordinates = result.get('coordinates', {})
                    measurements_data = result.get('measurements', [])
                    
                    # Extract pollutant values
                    pollutants = {}
                    for measurement in measurements_data:
                        parameter = measurement.get('parameter', '').lower()
                        value = measurement.get('value')
                        if value:
                            pollutants[parameter] = value
                    
                    # Calculate AQI from pollutants (simplified)
                    # OpenAQ may provide AQI directly, but if not, calculate from PM2.5
                    aqi_value = None
                    if 'pm25' in pollutants:
                        # Simplified AQI calculation from PM2.5 (US EPA formula)
                        pm25 = pollutants['pm25']
                        if pm25 <= 12:
                            aqi_value = int((pm25 / 12) * 50)
                        elif pm25 <= 35.4:
                            aqi_value = int(((pm25 - 12) / (35.4 - 12)) * (100 - 51) + 51)
                        elif pm25 <= 55.4:
                            aqi_value = int(((pm25 - 35.4) / (55.4 - 35.4)) * (150 - 101) + 101)
                        elif pm25 <= 150.4:
                            aqi_value = int(((pm25 - 55.4) / (150.4 - 55.4)) * (200 - 151) + 151)
                        else:
                            aqi_value = min(500, int(((pm25 - 150.4) / (250.4 - 150.4)) * (300 - 201) + 201))
                    
                    # Get coordinates
                    lat = coordinates.get('latitude')
                    lon = coordinates.get('longitude')
                    
                    if lat and lon:
                        measurement = {
                            'city_name': location.get('name', 'Unknown'),
                            'latitude': lat,
                            'longitude': lon,
                            'measured_at': datetime.fromisoformat(result.get('lastUpdated', datetime.utcnow().isoformat()).replace('Z', '+00:00')),
                            'aqi_value': aqi_value,
                            'pm25': pollutants.get('pm25'),
                            'pm10': pollutants.get('pm10'),
                            'o3': pollutants.get('o3'),
                            'no2': pollutants.get('no2'),
                            'co': pollutants.get('co'),
                            'so2': pollutants.get('so2'),
                            'source': 'OpenAQ',
                            'source_id': f"{location.get('id', '')}_{result.get('lastUpdated', '')}",
                            'url': f"https://openaq.org/#/location/{location.get('id', '')}",
                            'data_fetched_at': datetime.utcnow()
                        }
                        
                        # Try to match with city in database
                        city = City.query.filter_by(name=measurement['city_name']).first()
                        if city:
                            measurement['city_id'] = city.id
                        
                        measurements.append(measurement)
        
        except Exception as e:
            logger.error(f"OpenAQ API error: {e}")
        
        return measurements
    
    def _fetch_openweather_data(self, cities=None):
        """Fetch AQI data from OpenWeather API"""
        measurements = []
        
        try:
            # If no cities provided, use some default major cities
            if not cities:
                cities = [
                    {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060},
                    {'name': 'London', 'lat': 51.5074, 'lon': -0.1278},
                    {'name': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503},
                    {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522},
                    {'name': 'Sydney', 'lat': -33.8688, 'lon': 151.2093}
                ]
            
            for city in cities[:10]:  # Limit to 10 cities
                try:
                    url = f"{self.openweather_base_url}/air_pollution"
                    params = {
                        'lat': city.get('lat') or city['latitude'],
                        'lon': city.get('lon') or city['longitude'],
                        'appid': Config.OPENWEATHER_API_KEY
                    }
                    
                    response = requests.get(url, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'list' in data and len(data['list']) > 0:
                            air_data = data['list'][0]
                            components = air_data.get('components', {})
                            main = air_data.get('main', {})
                            dt = air_data.get('dt', 0)
                            
                            # OpenWeather provides AQI (1-5 scale), convert to 0-500
                            aqi_ow = main.get('aqi', 1)  # 1=good, 5=hazardous
                            aqi_value = self._convert_openweather_aqi(aqi_ow)
                            
                            measurement = {
                                'city_name': city.get('name', 'Unknown'),
                                'latitude': city.get('lat') or city['latitude'],
                                'longitude': city.get('lon') or city['longitude'],
                                'measured_at': datetime.fromtimestamp(dt),
                                'aqi_value': aqi_value,
                                'pm25': components.get('pm2_5'),
                                'pm10': components.get('pm10'),
                                'o3': components.get('o3'),
                                'no2': components.get('no2'),
                                'co': components.get('co') / 1000 if components.get('co') else None,  # Convert to ppm
                                'so2': components.get('so2'),
                                'source': 'OpenWeather',
                                'source_id': f"{city.get('name', '')}_{dt}",
                                'data_fetched_at': datetime.utcnow()
                            }
                            
                            # Try to match with city in database
                            city_db = City.query.filter_by(name=measurement['city_name']).first()
                            if city_db:
                                measurement['city_id'] = city_db.id
                            
                            measurements.append(measurement)
                    
                    # Small delay to respect rate limits
                    import time
                    time.sleep(0.2)
                
                except Exception as e:
                    logger.error(f"Error fetching OpenWeather data for {city.get('name', 'city')}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"OpenWeather API error: {e}")
        
        return measurements
    
    def _convert_openweather_aqi(self, aqi_ow):
        """Convert OpenWeather AQI (1-5) to standard AQI (0-500)"""
        # OpenWeather: 1=good, 2=fair, 3=moderate, 4=poor, 5=very poor
        conversion_map = {
            1: 25,   # Good
            2: 75,   # Fair
            3: 125,  # Moderate
            4: 225,  # Poor
            5: 400   # Very Poor
        }
        return conversion_map.get(aqi_ow, 100)
    
    def save_measurements_to_db(self, measurements):
        """Save AQI measurements to database"""
        saved_count = 0
        skipped_count = 0
        
        for measurement_data in measurements:
            try:
                # Check if measurement already exists
                existing = AQIMeasurement.query.filter_by(
                    source=measurement_data['source'],
                    source_id=measurement_data.get('source_id')
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in measurement_data.items():
                        if hasattr(existing, key) and key != 'id':
                            setattr(existing, key, value)
                    existing.data_fetched_at = datetime.utcnow()
                    skipped_count += 1
                else:
                    # Create new record
                    measurement = AQIMeasurement(**measurement_data)
                    db.session.add(measurement)
                    saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving AQI measurement to database: {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            logger.info(f"Saved {saved_count} new AQI measurements, skipped {skipped_count} duplicates")
            return {'saved': saved_count, 'skipped': skipped_count}
        except Exception as e:
            logger.error(f"Error committing AQI measurements to database: {e}")
            db.session.rollback()
            return {'saved': 0, 'skipped': 0, 'error': str(e)}


# Singleton instance
aqi_service = AQIService()
