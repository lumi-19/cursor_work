import requests
import psycopg2
from datetime import datetime
import time

# ================= DATABASE CONFIG =================

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "WebGis"
DB_USER = "postgres"
DB_PASSWORD = "Gondal.io"

# ================= NASA FIRMS ======================

NASA_FIRMS_API_KEY = "c19741ce74e91600c97f1b56edbbe101"
SOURCE = "VIIRS_SNPP_NRT"
DAYS = 1

# ==================================================

def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def fetch_tile(west, south, east, north, retries=3):
    url = (
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
        f"{NASA_FIRMS_API_KEY}/{SOURCE}/"
        f"{west},{south},{east},{north}/{DAYS}"
    )

    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            return r.text
        except requests.exceptions.ReadTimeout:
            print(f"⏳ Timeout for tile {west},{south},{east},{north} — retry {attempt+1}")
            time.sleep(5)

    return None

def parse_csv(text):
    lines = [l for l in text.splitlines() if l and not l.startswith("#")]
    if len(lines) < 2:
        return []

    header = lines[0].split(",")
    records = []

    for row in lines[1:]:
        values = row.split(",")
        if len(values) == len(header):
            records.append(dict(zip(header, values)))

    return records

def insert_records(records):
    conn = connect_db()
    cur = conn.cursor()
    inserted = skipped = 0

    for r in records:
        try:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
        except:
            skipped += 1
            continue

        acq_date = r.get("acq_date")
        acq_time = r.get("acq_time", "0000").zfill(4)

        try:
            occurred_at = datetime.strptime(
                f"{acq_date} {acq_time}", "%Y-%m-%d %H%M"
            )
        except:
            occurred_at = None

        source_id = f"{lat}_{lon}_{acq_date}_{acq_time}"

        cur.execute(
            "SELECT 1 FROM wildfires WHERE source_id = %s",
            (source_id,)
        )
        if cur.fetchone():
            skipped += 1
            continue

        brightness = None
        try:
            brightness = float(r.get("bright_ti4"))
        except:
            pass

        confidence = None
        try:
            confidence = int(r.get("confidence"))
        except:
            pass

        sql = """
        INSERT INTO wildfires (
            event_name,
            brightness,
            confidence,
            occurred_at,
            source,
            source_id,
            geom
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            ST_SetSRID(ST_MakePoint(%s, %s), 4326)
        )
        """

        cur.execute(sql, (
            "wildfire",
            brightness,
            confidence,
            occurred_at,
            "NASA_FIRMS",
            source_id,
            lon,
            lat
        ))

        inserted += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"Inserted: {inserted}, Skipped: {skipped}")

def main():
    # 30° × 30° tiles (safe size)
    tiles = []
    for lon in range(-180, 180, 30):
        for lat in range(-90, 90, 30):
            tiles.append((lon, lat, lon + 30, lat + 30))

    total_records = 0

    for west, south, east, north in tiles:
        print(f"📡 Fetching tile {west},{south},{east},{north}")
        csv_text = fetch_tile(west, south, east, north)

        if not csv_text:
            continue

        records = parse_csv(csv_text)
        total_records += len(records)

        if records:
            insert_records(records)

        time.sleep(1)  # be polite to FIRMS servers

    print(f"🔥 Total records fetched: {total_records}")

if __name__ == "__main__":
    main()
