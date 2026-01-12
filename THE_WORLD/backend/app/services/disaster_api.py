"""
THE_WORLD - Disaster API Service
Fetch disaster data from multiple external APIs
"""

import requests
from datetime import datetime, timedelta
from app.database import db
from app.models import Disaster
from app.config import Config
import logging

logger = logging.getLogger(__name__)


class DisasterAPIService:
    """Service for fetching disaster data from multiple sources"""
    
    def __init__(self):
        self.sources = {
            'usgs': self._fetch_usgs_earthquakes,
            'noaa': self._fetch_noaa_weather,
            'openweather': self._fetch_openweather_alerts
        }
    
    def fetch_all_disasters(self, days=7):
        """Fetch disasters from all available sources"""
        all_disasters = []
        
        # Fetch from USGS (Earthquakes)
        try:
            usgs_disasters = self._fetch_usgs_earthquakes(days)
            all_disasters.extend(usgs_disasters)
        except Exception as e:
            logger.error(f"Error fetching USGS data: {e}")
        
        # Fetch from NOAA (Weather disasters)
        try:
            noaa_disasters = self._fetch_noaa_weather(days)
            all_disasters.extend(noaa_disasters)
        except Exception as e:
            logger.error(f"Error fetching NOAA data: {e}")
        
        # Fetch from OpenWeather (Severe weather alerts)
        try:
            openweather_disasters = self._fetch_openweather_alerts(days)
            all_disasters.extend(openweather_disasters)
        except Exception as e:
            logger.error(f"Error fetching OpenWeather data: {e}")
        
        return all_disasters
    
    def _fetch_usgs_earthquakes(self, days=7):
        """Fetch earthquake data from USGS"""
        disasters = []
        
        try:
            # USGS Earthquake API - last N days
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
            params = {
                'format': 'geojson',
                'starttime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'endtime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'minmagnitude': 4.0,  # Minimum magnitude 4.0
                'orderby': 'time'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'features' in data:
                for feature in data['features']:
                    props = feature.get('properties', {})
                    coords = feature.get('geometry', {}).get('coordinates', [])
                    
                    if len(coords) >= 2:
                        disaster = {
                            'disaster_type': 'earthquake',
                            'title': props.get('title', 'Earthquake'),
                            'description': props.get('detail', ''),
                            'latitude': coords[1],
                            'longitude': coords[0],
                            'occurred_at': datetime.fromtimestamp(props.get('time', 0) / 1000),
                            'magnitude': props.get('mag'),
                            'severity': self._determine_severity(props.get('mag', 0), 'earthquake'),
                            'status': 'resolved',
                            'source': 'USGS',
                            'source_id': str(props.get('ids', '').split(',')[0]) if props.get('ids') else None,
                            'url': props.get('url', ''),
                            'data_fetched_at': datetime.utcnow()
                        }
                        disasters.append(disaster)
        
        except Exception as e:
            logger.error(f"USGS API error: {e}")
        
        return disasters
    
    def _fetch_noaa_weather(self, days=7):
        """Fetch severe weather data from NOAA"""
        disasters = []
        
        try:
            # NOAA Severe Weather API
            # Note: NOAA API structure may vary - this is a simplified version
            url = "https://www.weather.gov/documentation/services-web-api"
            
            # For now, return empty list as NOAA API requires specific endpoints
            # This can be implemented based on specific NOAA API endpoints available
            logger.info("NOAA weather data fetching - to be implemented with specific endpoints")
        
        except Exception as e:
            logger.error(f"NOAA API error: {e}")
        
        return disasters
    
    def _fetch_openweather_alerts(self, days=7):
        """Fetch severe weather alerts from OpenWeather"""
        disasters = []
        
        try:
            # OpenWeather One Call API for weather alerts
            # Note: This requires city coordinates - for demo, using major cities
            # In production, iterate through cities or use bounding box
            
            # Example: Using New York coordinates (can be expanded)
            lat, lon = 40.7128, -74.0060
            
            url = "https://api.openweathermap.org/data/2.5/onecall"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': Config.OPENWEATHER_API_KEY,
                'exclude': 'current,minutely,hourly'
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for alerts
                alerts = data.get('alerts', [])
                for alert in alerts:
                    disaster = {
                        'disaster_type': self._map_alert_to_disaster_type(alert.get('event', '')),
                        'title': alert.get('event', 'Weather Alert'),
                        'description': alert.get('description', ''),
                        'latitude': lat,
                        'longitude': lon,
                        'occurred_at': datetime.fromtimestamp(alert.get('start', 0)),
                        'severity': 'medium',
                        'status': 'active',
                        'source': 'OpenWeather',
                        'source_id': f"{alert.get('sender_name', '')}_{alert.get('start', 0)}",
                        'data_fetched_at': datetime.utcnow()
                    }
                    disasters.append(disaster)
        
        except Exception as e:
            logger.error(f"OpenWeather API error: {e}")
        
        return disasters
    
    def _map_alert_to_disaster_type(self, alert_event):
        """Map OpenWeather alert event to disaster type"""
        alert_lower = alert_event.lower()
        
        if 'hurricane' in alert_lower or 'cyclone' in alert_lower:
            return 'hurricane'
        elif 'tornado' in alert_lower:
            return 'tornado'
        elif 'flood' in alert_lower:
            return 'flood'
        elif 'wildfire' in alert_lower or 'fire' in alert_lower:
            return 'wildfire'
        elif 'storm' in alert_lower:
            return 'storm'
        else:
            return 'storm'  # Default
    
    def _determine_severity(self, magnitude, disaster_type):
        """Determine severity based on magnitude/type"""
        if disaster_type == 'earthquake':
            if magnitude >= 7.0:
                return 'critical'
            elif magnitude >= 5.5:
                return 'high'
            elif magnitude >= 4.5:
                return 'medium'
            else:
                return 'low'
        else:
            return 'medium'  # Default
    
    def save_disasters_to_db(self, disasters):
        """Save disaster data to database"""
        saved_count = 0
        skipped_count = 0
        
        for disaster_data in disasters:
            try:
                # Check if disaster already exists
                existing = Disaster.query.filter_by(
                    source=disaster_data['source'],
                    source_id=disaster_data.get('source_id')
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in disaster_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.data_fetched_at = datetime.utcnow()
                    skipped_count += 1
                else:
                    # Create new record
                    disaster = Disaster(**disaster_data)
                    db.session.add(disaster)
                    saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving disaster to database: {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            logger.info(f"Saved {saved_count} new disasters, skipped {skipped_count} duplicates")
            return {'saved': saved_count, 'skipped': skipped_count}
        except Exception as e:
            logger.error(f"Error committing disasters to database: {e}")
            db.session.rollback()
            return {'saved': 0, 'skipped': 0, 'error': str(e)}


# Singleton instance
disaster_api_service = DisasterAPIService()
