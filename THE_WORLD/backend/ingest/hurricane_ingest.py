import csv
import os
import psycopg2
import requests
from datetime import datetime
from dotenv import load_dotenv

# ==================================================
# LOAD .env FILE (EXPLICIT PATH)
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")  # adjust if needed
load_dotenv(ENV_PATH)

# ==================================================
# DATABASE CONFIG FROM .env
# ==================================================

DB_HOST = os.getenv("POSTGIS_HOST")
DB_PORT = os.getenv("POSTGIS_PORT")
DB_NAME = os.getenv("POSTGIS_DB")
DB_USER = os.getenv("POSTGIS_USER")
DB_PASSWORD = os.getenv("POSTGIS_PASSWORD")

# ==================================================
# DATA SOURCE (IBTrACS)
# ==================================================

IBTRACS_URL = (
    "https://www.ncei.noaa.gov/data/"
    "international-best-track-archive-for-climate-stewardship-ibtracs/"
    "v04r00/access/csv/ibtracs.ALL.list.v04r00.csv"
)

SOURCE_NAME = "NOAA_IBTrACS"
MAX_RECORDS = 1000          # 🔥 HARD LIMIT
MIN_YEAR = 2015             # recent data only

# ==================================================

def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def fetch_ibtracs_lines():
    print("🌪️ Downloading IBTrACS data (streaming)...")
    response = requests.get(IBTRACS_URL, stream=True, timeout=120)
    response.raise_for_status()
    return response.iter_lines(decode_unicode=True)

def parse_datetime(iso_time):
    try:
        return datetime.strptime(iso_time, "%Y-%m-%d %H:%M:%S")
    except:
        return None

def determine_severity(wind):
    if wind is None:
        return None
    if wind >= 137:
        return "Category 5"
    elif wind >= 113:
        return "Category 4"
    elif wind >= 96:
        return "Category 3"
    elif wind >= 83:
        return "Category 2"
    elif wind >= 64:
        return "Category 1"
    else:
        return "Tropical Storm"

def insert_hurricanes(lines):
    conn = connect_db()
    cur = conn.cursor()
    reader = csv.DictReader(lines)

    inserted = 0
    skipped = 0

    for row in reader:
        if inserted >= MAX_RECORDS:
            print(f"🛑 Reached limit: {MAX_RECORDS} hurricanes")
            break

        occurred_at = parse_datetime(row.get("ISO_TIME"))
        if not occurred_at or occurred_at.year < MIN_YEAR:
            skipped += 1
            continue

        try:
            lat = float(row["LAT"])
            lon = float(row["LON"])
        except:
            skipped += 1
            continue

        try:
            wind_speed = float(row["USA_WIND"])
        except:
            wind_speed = None

        try:
            pressure = float(row["USA_PRES"])
        except:
            pressure = None

        category = row.get("USA_SSHS")
        if category == "-999":
            category = None

        severity = determine_severity(wind_speed)
        source_id = f"{row['SID']}_{row['ISO_TIME']}"

        cur.execute(
            "SELECT 1 FROM hurricanes WHERE source_id = %s",
            (source_id,)
        )
        if cur.fetchone():
            skipped += 1
            continue

        cur.execute("""
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
                geom
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
        """, (
            row["NAME"] if row["NAME"] != "NOT NAMED" else "Hurricane",
            "hurricane",
            category,
            wind_speed,
            pressure,
            occurred_at,
            severity,
            SOURCE_NAME,
            source_id,
            lon,
            lat
        ))

        inserted += 1

        if inserted % 100 == 0:
            print(f"Inserted {inserted} hurricanes...")

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ Finished | Inserted: {inserted}, Skipped: {skipped}")

def main():
    lines = fetch_ibtracs_lines()
    insert_hurricanes(lines)

if __name__ == "__main__":
    main()
