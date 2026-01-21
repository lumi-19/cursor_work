import requests
import psycopg2
from datetime import datetime
from psycopg2 import sql

# ===== HARDCODED DATABASE CREDENTIALS =====
DB_USER = "postgres"
DB_PASSWORD = "Gondal.io"
DB_NAME = "WebGis"
DB_HOST = "localhost"
DB_PORT = 5432

# NASA EONET API for Severe Storms (Hurricanes, Cyclones, Typhoons)
HURRICANE_URL = "https://eonet.gsfc.nasa.gov/api/v3/events?category=severeStorms&status=open"

# ------------------------------------------------

def fetch_hurricane_data():
    """Fetch active storm data from NASA EONET"""
    try:
        print(f"📡 Connecting to NASA EONET ({HURRICANE_URL})...")
        response = requests.get(HURRICANE_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("events", [])
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return []


def connect_db():
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except Exception as e:
        print("❌ Could not connect to the database.")
        print(f"   Error: {e}")
        return None


def determine_category_and_severity(wind_knots):
    """
    Determine Hurricane Category (Saffir-Simpson Scale) 
    and Severity based on wind speed in Knots.
    """
    if wind_knots is None:
        return "Unknown", "Unknown"

    # Saffir-Simpson Scale (Knots)
    if wind_knots < 34:
        return "Tropical Depression", "Low"
    elif wind_knots < 64:
        return "Tropical Storm", "Moderate"
    elif wind_knots < 83:
        return "Category 1", "High"
    elif wind_knots < 96:
        return "Category 2", "High"
    elif wind_knots < 113:
        return "Category 3", "Very High"
    elif wind_knots < 137:
        return "Category 4", "Severe"
    else:
        return "Category 5", "Catastrophic"


def insert_hurricanes(events):
    conn = connect_db()
    if conn is None:
        return

    cur = conn.cursor()

    inserted = 0
    skipped = 0

    print(f"🔄 Processing {len(events)} active storms...")

    for event in events:
        # 1. Extract Basic Info
        # EONET ID (e.g., "EONET_6299")
        source_id = event.get("id") 
        event_name = event.get("title", "Unknown Storm")

        # 2. Extract Geometry & Date
        # Storms have a "track" (multiple points). We want the LATEST position.
        geometries = event.get("geometry", [])
        if not geometries:
            skipped += 1
            continue

        latest_geo = geometries[-1] # Get the last item in the list
        coords = latest_geo.get("coordinates", [])
        date_str = latest_geo.get("date")

        if len(coords) < 2:
            skipped += 1
            continue
        
        lon, lat = coords[0], coords[1]

        # 3. Parse Date
        occurred_at = None
        if date_str:
            try:
                occurred_at = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                occurred_at = datetime.utcnow()

        # 4. Extract/Calculate Physics (Wind/Pressure)
        # EONET typically puts wind speed in 'magnitudeValue' if available
        wind_speed = latest_geo.get("magnitudeValue")
        magnitude_unit = latest_geo.get("magnitudeUnit")

        # Convert to Knots if unit is usually 'kts'. 
        # If unit is missing, we assume knots for storms in this API.
        # If API returns None, wind_speed remains None.
        
        pressure = None # EONET API rarely provides pressure in the simple view

        # 5. Determine Category & Severity
        category, severity = determine_category_and_severity(wind_speed)

        # 6. Check Duplicate
        # We only store the storm once per ID. 
        # (To store the track, you would need a separate 'track' table)
        cur.execute(
            "SELECT 1 FROM hurricanes WHERE source_id = %s LIMIT 1;",
            (source_id,)
        )
        if cur.fetchone():
            skipped += 1
            continue

        # 7. INSERT Query
        insert_sql = """
            INSERT INTO hurricanes (
                event_name,
                disaster_type,
                category,
                wind_speed,
                pressure,
                occurred_at,
                severity,
                source,
                source_id,
                geom,
                created_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                CURRENT_TIMESTAMP
            );
        """

        values = (
            event_name,         # event_name
            "hurricane",        # disaster_type
            category,           # category
            wind_speed,         # wind_speed (float)
            pressure,           # pressure (float/null)
            occurred_at,        # occurred_at
            severity,           # severity
            "NASA EONET",       # source
            source_id,          # source_id
            lon,                # geom (lon)
            lat                 # geom (lat)
        )

        try:
            cur.execute(insert_sql, values)
            inserted += 1
        except Exception as e:
            print(f"❌ Insert failed for {event_name}: {e}")
            conn.rollback()
        else:
            conn.commit()

    cur.close()
    conn.close()

    print("-" * 30)
    print(f"✅ Successfully Inserted: {inserted}")
    print(f"⏭  Skipped (Duplicates/No Geom): {skipped}")
    print("-" * 30)


def main():
    print("🚀 Starting Hurricane Ingestion (NASA EONET → PostGIS)")
    events = fetch_hurricane_data()
    
    if events:
        insert_hurricanes(events)
    else:
        print("⚠️ No active storms found in API.")
        
    print("✅ Ingestion complete")


if __name__ == "__main__":
    main()