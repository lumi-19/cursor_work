import os
import requests
import psycopg2
from psycopg2 import sql
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load .env
load_dotenv()

# ===== READ EXACT VARIABLES FROM YOUR .env =====
DB_USER = os.getenv("POSTGIS_USER")
DB_PASSWORD = os.getenv("POSTGIS_PASSWORD")
DB_NAME = os.getenv("POSTGIS_DB")
DB_HOST = os.getenv("POSTGIS_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGIS_PORT", 5432))

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# ------------------------------------------------

def fetch_usgs_data():
    """Fetch last 1 day earthquake data from USGS"""
    end = datetime.utcnow()
    start = end - timedelta(days=1)

    params = {
        "format": "geojson",
        "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": end.strftime("%Y-%m-%dT%H:%M:%S"),
        "orderby": "time",
        "limit": 500
    }

    response = requests.get(USGS_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("features", [])


def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def insert_disasters(features):
    conn = connect_db()
    cur = conn.cursor()

    inserted = 0
    skipped = 0

    for feature in features:
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

        source_id = feature.get("id")
        if not source_id:
            skipped += 1
            continue

        # Convert time (ms → timestamp)
        time_ms = props.get("time")
        occurred_at = None
        if time_ms:
            occurred_at = datetime.fromtimestamp(
                time_ms / 1000, tz=timezone.utc
            ).replace(tzinfo=None)

        magnitude = props.get("mag")
        magnitude = float(magnitude) if magnitude is not None else None

        place = props.get("place")
        title = props.get("title")
        url = props.get("url")

        # Severity logic (simple & explainable in exams)
        severity = None
        if magnitude is not None:
            if magnitude >= 7:
                severity = "very_high"
            elif magnitude >= 5:
                severity = "high"
            elif magnitude >= 3:
                severity = "moderate"
            else:
                severity = "low"

        # Check duplicate
        cur.execute(
            "SELECT 1 FROM disasters WHERE source_id = %s LIMIT 1;",
            (source_id,)
        )
        if cur.fetchone():
            skipped += 1
            continue

        # INSERT using PostGIS geometry
        insert_sql = """
            INSERT INTO disasters (
                disaster_type,
                title,
                description,
                latitude,
                longitude,
                geom,
                occurred_at,
                magnitude,
                severity,
                source,
                source_id,
                url,
                created_at,
                updated_at,
                data_fetched_at
            )
            VALUES (
                %s, %s, %s, %s, %s,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                %s, %s, %s, %s, %s, %s,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            );
        """

        values = (
            "earthquake",
            title,
            place,
            lat,
            lon,
            lon,  # IMPORTANT: lon first
            lat,
            occurred_at,
            magnitude,
            severity,
            "USGS",
            source_id,
            url
        )

        try:
            cur.execute(insert_sql, values)
            inserted += 1
        except Exception as e:
            print(f"❌ Insert failed for {source_id}: {e}")
            conn.rollback()
        else:
            conn.commit()

    cur.close()
    conn.close()

    print(f"✅ Inserted: {inserted}")
    print(f"⏭ Skipped: {skipped}")


def main():
    print("🚀 Starting Disaster Ingestion (USGS → PostGIS)")
    features = fetch_usgs_data()
    print(f"🌍 Fetched {len(features)} records from USGS")
    insert_disasters(features)
    print("✅ Ingestion complete")


if __name__ == "__main__":
    main()
