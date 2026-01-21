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

# NOAA NCEI (NGDC) Tsunami API
# Fetching events from 2010 onwards
TSUNAMI_URL = "https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events?minYear=2010"

# ------------------------------------------------

def fetch_tsunami_data():
    """Fetch tsunami data from NOAA NCEI"""
    try:
        print(f"📡 Connecting to NOAA API ({TSUNAMI_URL})...")
        response = requests.get(TSUNAMI_URL, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
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


def calculate_severity(height_meters):
    """Determine severity based on wave height"""
    if height_meters is None:
        return "Unknown"
    
    if height_meters < 0.5:
        return "Low"
    elif height_meters < 2.0:
        return "Moderate"
    elif height_meters < 5.0:
        return "High"
    else:
        return "Very High"


def insert_tsunamis(events):
    conn = connect_db()
    if conn is None:
        return

    cur = conn.cursor()

    inserted = 0
    skipped = 0

    print(f"🔄 Processing {len(events)} records...")

    for event in events:
        # 1. Extract & Construct Basic Info
        source_id = str(event.get("id"))
        
        country = event.get("country", "")
        loc_name = event.get("locationName", "")
        # Construct a title like: "Tsunami in Japan, Fukushima"
        event_name = f"{country}, {loc_name}".strip(", ")
        if not event_name:
            event_name = "Unknown Tsunami Event"

        wave_height = event.get("maxWaterHeight") # In meters
        
        # 2. Extract Geometry
        lat = event.get("latitude")
        lon = event.get("longitude")

        # Skip if no coordinates
        if lat is None or lon is None:
            skipped += 1
            continue

        # 3. Construct Date (NOAA gives Year, Month, Day, Hour separately)
        year = event.get("year")
        # Handle cases where month/day/time might be missing in older records
        month = event.get("month") if event.get("month") else 1
        day = event.get("day") if event.get("day") else 1
        hour = event.get("hour") if event.get("hour") else 0
        minute = event.get("minute") if event.get("minute") else 0
        
        occurred_at = None
        if year:
            try:
                occurred_at = datetime(year, month, day, hour, minute)
            except ValueError:
                occurred_at = datetime(year, 1, 1)

        # 4. Calculate Severity
        severity = calculate_severity(wave_height)

        # 5. Check for Duplicates
        cur.execute(
            "SELECT 1 FROM tsunamis WHERE source_id = %s LIMIT 1;",
            (source_id,)
        )
        if cur.fetchone():
            skipped += 1
            continue

        # 6. INSERT Query (Matching your specific schema)
        insert_sql = """
            INSERT INTO tsunamis (
                event_name,
                disaster_type,
                wave_height,
                occurred_at,
                severity,
                source,
                source_id,
                geom,
                created_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                CURRENT_TIMESTAMP
            );
        """

        values = (
            event_name,         # event_name
            "tsunami",          # disaster_type
            wave_height,        # wave_height (float)
            occurred_at,        # occurred_at
            severity,           # severity (calculated above)
            "NOAA",             # source
            source_id,          # source_id
            lon,                # geom (lon)
            lat                 # geom (lat)
        )

        try:
            cur.execute(insert_sql, values)
            inserted += 1
        except Exception as e:
            print(f"❌ Insert failed for ID {source_id}: {e}")
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
    print("🚀 Starting Tsunami Ingestion (NOAA → PostGIS)")
    events = fetch_tsunami_data()
    
    if events:
        insert_tsunamis(events)
    else:
        print("⚠️ No data found.")
        
    print("✅ Ingestion complete")


if __name__ == "__main__":
    main()