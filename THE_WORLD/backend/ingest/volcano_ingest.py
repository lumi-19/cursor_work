import requests
import psycopg2
from datetime import datetime

# ===== HARDCODED DATABASE CREDENTIALS =====
DB_USER = "postgres"
DB_PASSWORD = "Gondal.io"
DB_NAME = "WebGis"
DB_HOST = "localhost"
DB_PORT = 5432

# NASA EONET API URL for Volcanoes
# Returns active volcanic events globally
VOLCANO_URL = "https://eonet.gsfc.nasa.gov/api/v3/events?category=volcanoes&status=open"

# ------------------------------------------------

def fetch_volcano_data():
    """Fetch active volcano data from NASA EONET"""
    try:
        print(f"📡 Connecting to {VOLCANO_URL}...")
        response = requests.get(VOLCANO_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("events", [])
    except Exception as e:
        print(f"❌ Error fetching data from API: {e}")
        return []


def connect_db():
    """Connect to PostGIS using hardcoded credentials"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print("❌ Could not connect to the database.")
        print(f"   Error: {e}")
        return None


def insert_volcanoes(events):
    conn = connect_db()
    if conn is None:
        return

    cur = conn.cursor()

    inserted = 0
    skipped = 0

    print(f"🔄 Processing {len(events)} events...")

    for event in events:
        # 1. Extract Basic Info
        source_id = event.get("id")
        volcano_name = event.get("title", "Unknown Volcano")
        
        # NASA EONET provides a sources list, we grab the link for reference
        sources_list = event.get("sources", [])
        source_url = sources_list[0].get("url") if sources_list else "https://eonet.gsfc.nasa.gov"

        # 2. Extract Geometry (NASA returns a list of points, we take the latest)
        geometries = event.get("geometry", [])
        if not geometries:
            skipped += 1
            continue
        
        # Get the most recent observation (usually the last in the list)
        latest_geo = geometries[-1]
        coords = latest_geo.get("coordinates", []) # [lon, lat]
        date_str = latest_geo.get("date") # ISO 8601 string

        # Ensure we have valid coordinates
        if len(coords) < 2:
            skipped += 1
            continue

        lon, lat = coords[0], coords[1]

        # 3. Handle Date Parsing
        occurred_at = None
        if date_str:
            try:
                # EONET format example: "2023-12-18T14:00:00Z"
                occurred_at = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                occurred_at = datetime.utcnow()

        # 4. Set Schema Fields
        # Elevation: API doesn't provide it, so we leave it NULL
        elevation = None 
        
        # Severity: API doesn't provide numeric magnitude, setting generic default
        severity = "Unknown" 
        
        # Status: We queried for 'open' events, so they are Active
        status = "Active"

        # 5. Check for Duplicates (based on source_id)
        cur.execute(
            "SELECT 1 FROM volcanoes WHERE source_id = %s LIMIT 1;",
            (source_id,)
        )
        if cur.fetchone():
            skipped += 1
            continue

        # 6. INSERT Query
        insert_sql = """
            INSERT INTO volcanoes (
                volcano_name,
                disaster_type,
                status,
                elevation,
                occurred_at,
                severity,
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
            volcano_name,       # volcano_name
            "volcanic_eruption",# disaster_type
            status,             # status
            elevation,          # elevation
            occurred_at,        # occurred_at
            severity,           # severity
            "NASA EONET",       # source
            source_id,          # source_id
            lon,                # geom (longitude)
            lat                 # geom (latitude)
        )

        try:
            cur.execute(insert_sql, values)
            inserted += 1
        except Exception as e:
            print(f"❌ Insert failed for {volcano_name}: {e}")
            conn.rollback()
        else:
            conn.commit()

    cur.close()
    conn.close()

    print("-" * 30)
    print(f"✅ Successfully Inserted: {inserted}")
    print(f"⏭  Skipped (Duplicate/No Geom): {skipped}")
    print("-" * 30)


def main():
    print("🚀 Starting Volcano Ingestion (NASA EONET → PostGIS)")
    events = fetch_volcano_data()
    
    if events:
        print(f"🌍 Found {len(events)} events from API.")
        insert_volcanoes(events)
    else:
        print("⚠️ No data found or API request failed.")

    print("✅ Ingestion script finished.")


if __name__ == "__main__":
    main()