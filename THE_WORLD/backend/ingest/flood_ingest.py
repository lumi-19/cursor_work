import os
import requests
import psycopg2
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# Load .env
load_dotenv()

# ===== READ EXACT VARIABLES FROM YOUR .env =====
DB_USER = os.getenv("POSTGIS_USER")
DB_PASSWORD = os.getenv("POSTGIS_PASSWORD")
DB_NAME = os.getenv("POSTGIS_DB")  # Your floods database
DB_HOST = os.getenv("POSTGIS_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGIS_PORT", 5432))

# GDACS API for flood events (GeoJSON format)
GDACS_FLOODS_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"

# Alternative: ReliefWeb API
RELIEFWEB_URL = "https://api.reliefweb.int/v1/disasters"

# ------------------------------------------------


def fetch_gdacs_floods():
    """Fetch flood data from GDACS API"""
    end = datetime.utcnow()
    start = end - timedelta(days=30)  # Last 30 days for floods

    params = {
        "eventlist": "FL",  # FL = Floods
        "fromDate": start.strftime("%Y-%m-%d"),
        "toDate": end.strftime("%Y-%m-%d"),
        "alertlevel": "Green;Orange;Red",  # All alert levels
    }

    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.get(GDACS_FLOODS_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        features = data.get("features", [])
        print(f"📥 GDACS returned {len(features)} flood events")
        return features
    except Exception as e:
        print(f"⚠️ GDACS fetch failed: {e}")
        return []


def fetch_reliefweb_floods():
    """Fetch flood data from ReliefWeb API as backup source"""
    end = datetime.utcnow()
    start = end - timedelta(days=30)

    params = {
        "appname": "flood-ingestion",
        "filter[field]": "type",
        "filter[value]": "Flood",
        "filter[operator]": "AND",
        "fields[include][]": ["name", "date", "country", "glide", "status", "primary_type"],
        "limit": 100,
        "sort[]": "date:desc"
    }

    # ReliefWeb uses POST for complex queries
    payload = {
        "filter": {
            "operator": "AND",
            "conditions": [
                {
                    "field": "type",
                    "value": "Flood"
                },
                {
                    "field": "date.created",
                    "value": {
                        "from": start.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                        "to": end.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                    }
                }
            ]
        },
        "fields": {
            "include": ["name", "date", "country", "glide", "status", "primary_type", "description"]
        },
        "limit": 100,
        "sort": ["date.created:desc"]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(RELIEFWEB_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        disasters = data.get("data", [])
        print(f"📥 ReliefWeb returned {len(disasters)} flood events")
        return disasters
    except Exception as e:
        print(f"⚠️ ReliefWeb fetch failed: {e}")
        return []


def fetch_floodlist_gdacs():
    """
    Fetch from GDACS GeoRSS feed and parse flood events
    This is a more reliable endpoint
    """
    url = "https://www.gdacs.org/xml/rss.xml"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        floods = []
        
        # Define namespaces
        namespaces = {
            'gdacs': 'http://www.gdacs.org',
            'geo': 'http://www.w3.org/2003/01/geo/wgs84_pos#',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        
        for item in root.findall('.//item'):
            event_type = item.find('gdacs:eventtype', namespaces)
            
            # Only process floods (FL)
            if event_type is not None and event_type.text == 'FL':
                flood = {
                    'title': item.find('title').text if item.find('title') is not None else None,
                    'description': item.find('description').text if item.find('description') is not None else None,
                    'link': item.find('link').text if item.find('link') is not None else None,
                    'pubDate': item.find('pubDate').text if item.find('pubDate') is not None else None,
                    'lat': item.find('geo:lat', namespaces).text if item.find('geo:lat', namespaces) is not None else None,
                    'lon': item.find('geo:long', namespaces).text if item.find('geo:long', namespaces) is not None else None,
                    'eventid': item.find('gdacs:eventid', namespaces).text if item.find('gdacs:eventid', namespaces) is not None else None,
                    'alertlevel': item.find('gdacs:alertlevel', namespaces).text if item.find('gdacs:alertlevel', namespaces) is not None else None,
                    'country': item.find('gdacs:country', namespaces).text if item.find('gdacs:country', namespaces) is not None else None,
                    'severity': item.find('gdacs:severity', namespaces).text if item.find('gdacs:severity', namespaces) is not None else None,
                }
                floods.append(flood)
        
        print(f"📥 GDACS RSS returned {len(floods)} flood events")
        return floods
        
    except Exception as e:
        print(f"⚠️ GDACS RSS fetch failed: {e}")
        return []


def connect_db():
    """Connect to PostGIS database"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def parse_severity(alert_level, severity_text):
    """Convert GDACS alert level to severity"""
    if alert_level:
        alert_level = alert_level.lower()
        if alert_level == 'red':
            return 'very_high'
        elif alert_level == 'orange':
            return 'high'
        elif alert_level == 'green':
            return 'moderate'
    
    if severity_text:
        severity_text = severity_text.lower()
        if 'extreme' in severity_text or 'severe' in severity_text:
            return 'very_high'
        elif 'high' in severity_text or 'major' in severity_text:
            return 'high'
        elif 'moderate' in severity_text or 'medium' in severity_text:
            return 'moderate'
    
    return 'low'


def parse_date(date_str):
    """Parse various date formats"""
    if not date_str:
        return None
    
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",  # RSS format
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo:
                dt = dt.replace(tzinfo=None)
            return dt
        except ValueError:
            continue
    
    return None


def insert_floods_from_rss(floods):
    """Insert flood data from GDACS RSS feed"""
    conn = connect_db()
    cur = conn.cursor()

    inserted = 0
    skipped = 0

    for flood in floods:
        try:
            lat = flood.get('lat')
            lon = flood.get('lon')

            if lat is None or lon is None:
                skipped += 1
                continue

            lat = float(lat)
            lon = float(lon)

            source_id = flood.get('eventid')
            if not source_id:
                source_id = f"gdacs_fl_{hash(flood.get('title', ''))}"

            # Check duplicate
            cur.execute(
                "SELECT 1 FROM floods WHERE source_id = %s LIMIT 1;",
                (source_id,)
            )
            if cur.fetchone():
                skipped += 1
                continue

            event_name = flood.get('title')
            country = flood.get('country')
            severity = parse_severity(flood.get('alertlevel'), flood.get('severity'))
            affected_area = flood.get('description')
            occurred_at = parse_date(flood.get('pubDate'))

            # INSERT using PostGIS geometry
            insert_sql = """
                INSERT INTO floods (
                    event_name,
                    country,
                    disaster_type,
                    severity,
                    affected_area,
                    occurred_at,
                    source,
                    source_id,
                    geom,
                    created_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    CURRENT_TIMESTAMP
                );
            """

            values = (
                event_name,
                country,
                'flood',
                severity,
                affected_area,
                occurred_at,
                'GDACS',
                source_id,
                lon,  # IMPORTANT: lon first for ST_MakePoint
                lat,
            )

            cur.execute(insert_sql, values)
            inserted += 1
            conn.commit()

        except Exception as e:
            print(f"❌ Insert failed for flood event: {e}")
            conn.rollback()
            skipped += 1

    cur.close()
    conn.close()

    print(f"✅ Inserted: {inserted}")
    print(f"⏭ Skipped: {skipped}")
    
    return inserted, skipped


def insert_floods_from_gdacs_api(features):
    """Insert flood data from GDACS GeoJSON API"""
    conn = connect_db()
    cur = conn.cursor()

    inserted = 0
    skipped = 0

    for feature in features:
        try:
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [])

            if len(coords) < 2:
                skipped += 1
                continue

            lon, lat = coords[0], coords[1]

            if lon is None or lat is None:
                skipped += 1
                continue

            source_id = props.get("eventid") or feature.get("id")
            if not source_id:
                skipped += 1
                continue

            source_id = f"gdacs_{source_id}"

            # Check duplicate
            cur.execute(
                "SELECT 1 FROM floods WHERE source_id = %s LIMIT 1;",
                (source_id,)
            )
            if cur.fetchone():
                skipped += 1
                continue

            event_name = props.get("name") or props.get("eventname")
            country = props.get("country")
            severity = parse_severity(props.get("alertlevel"), props.get("severitydata"))
            affected_area = props.get("description") or props.get("htmldescription")
            
            # Parse date
            date_str = props.get("fromdate") or props.get("todate")
            occurred_at = parse_date(date_str)

            # INSERT using PostGIS geometry
            insert_sql = """
                INSERT INTO floods (
                    event_name,
                    country,
                    disaster_type,
                    severity,
                    affected_area,
                    occurred_at,
                    source,
                    source_id,
                    geom,
                    created_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    CURRENT_TIMESTAMP
                );
            """

            values = (
                event_name,
                country,
                'flood',
                severity,
                affected_area,
                occurred_at,
                'GDACS',
                source_id,
                lon,
                lat,
            )

            cur.execute(insert_sql, values)
            inserted += 1
            conn.commit()

        except Exception as e:
            print(f"❌ Insert failed for {source_id}: {e}")
            conn.rollback()
            skipped += 1

    cur.close()
    conn.close()

    print(f"✅ Inserted: {inserted}")
    print(f"⏭ Skipped: {skipped}")
    
    return inserted, skipped


def main():
    print("=" * 50)
    print("🌊 Starting Flood Data Ingestion (GDACS → PostGIS)")
    print("=" * 50)
    
    total_inserted = 0
    total_skipped = 0
    
    # Method 1: Try GDACS RSS feed (most reliable)
    print("\n📡 Fetching from GDACS RSS Feed...")
    rss_floods = fetch_floodlist_gdacs()
    if rss_floods:
        ins, skip = insert_floods_from_rss(rss_floods)
        total_inserted += ins
        total_skipped += skip
    
    # Method 2: Try GDACS API (GeoJSON)
    print("\n📡 Fetching from GDACS API...")
    api_floods = fetch_gdacs_floods()
    if api_floods:
        ins, skip = insert_floods_from_gdacs_api(api_floods)
        total_inserted += ins
        total_skipped += skip
    
    print("\n" + "=" * 50)
    print(f"🏁 Ingestion Complete!")
    print(f"   Total Inserted: {total_inserted}")
    print(f"   Total Skipped: {total_skipped}")
    print("=" * 50)


if __name__ == "__main__":
    main()