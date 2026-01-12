# Software Requirements Specification (SRS)
# WebGIS Disaster and AQI Monitoring System
## Part 3: Database Design

---

## 6. Database Design

### 6.1 Database Overview

The system uses PostgreSQL with PostGIS extension as the spatial database for storing disaster events, AQI measurements, city information, and related spatial data. PostGIS provides spatial data types, spatial indexing, and spatial functions for efficient geographic data management.

### 6.2 Database Schema Design

**6.2.1 Schema Structure**

The database schema consists of the following main tables:

1. **cities** - City information and boundaries
2. **disasters** - Disaster event records
3. **aqi_measurements** - AQI measurement records
4. **disaster_aqi_correlation** - Correlation analysis results (optional, can be computed on-the-fly)

---

### 6.3 Table Definitions

#### 6.3.1 Cities Table

**Table Name:** `cities`

**Purpose:** Store city information including name, location, and geographic boundaries.

**Schema:**

```sql
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    country_code VARCHAR(2),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    geom GEOMETRY(POINT, 4326),  -- PostGIS point geometry (WGS84)
    boundary GEOMETRY(POLYGON, 4326),  -- Optional city boundary polygon
    population INTEGER,
    timezone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index on point geometry
CREATE INDEX idx_cities_geom ON cities USING GIST (geom);

-- Create spatial index on boundary polygon (if used)
CREATE INDEX idx_cities_boundary ON cities USING GIST (boundary);

-- Create index on name for faster searches
CREATE INDEX idx_cities_name ON cities (name);
CREATE INDEX idx_cities_country ON cities (country);
```

**Fields:**
- `id`: Primary key (auto-increment)
- `name`: City name (e.g., "New York", "London")
- `country`: Country name
- `country_code`: ISO country code (e.g., "US", "GB")
- `latitude`: Latitude coordinate (decimal degrees)
- `longitude`: Longitude coordinate (decimal degrees)
- `geom`: PostGIS POINT geometry (SRID 4326 - WGS84)
- `boundary`: PostGIS POLYGON geometry for city boundaries (optional)
- `population`: City population (optional)
- `timezone`: Timezone identifier (optional)
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

**Constraints:**
- `name` and `country` are required
- `latitude` and `longitude` are required
- Unique constraint on (name, country) combination (optional)

---

#### 6.3.2 Disasters Table

**Table Name:** `disasters`

**Purpose:** Store disaster event records with spatial location and attributes.

**Schema:**

```sql
CREATE TABLE disasters (
    id SERIAL PRIMARY KEY,
    disaster_type VARCHAR(50) NOT NULL,
    title VARCHAR(500),
    description TEXT,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    geom GEOMETRY(POINT, 4326),  -- PostGIS point geometry
    occurred_at TIMESTAMP NOT NULL,
    magnitude DECIMAL(10, 2),  -- For earthquakes, etc.
    severity VARCHAR(50),  -- low, medium, high, etc.
    status VARCHAR(50),  -- active, resolved, etc.
    source VARCHAR(255),  -- API source name
    source_id VARCHAR(255),  -- External API ID
    url TEXT,  -- Link to detailed information
    affected_area GEOMETRY(POLYGON, 4326),  -- Optional affected area polygon
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fetched_at TIMESTAMP  -- When data was fetched from API
);

-- Create spatial index on point geometry
CREATE INDEX idx_disasters_geom ON disasters USING GIST (geom);

-- Create indexes for common queries
CREATE INDEX idx_disasters_type ON disasters (disaster_type);
CREATE INDEX idx_disasters_occurred_at ON disasters (occurred_at);
CREATE INDEX idx_disasters_source_id ON disasters (source, source_id);
CREATE INDEX idx_disasters_status ON disasters (status);

-- Composite index for date range queries
CREATE INDEX idx_disasters_type_date ON disasters (disaster_type, occurred_at);
```

**Fields:**
- `id`: Primary key (auto-increment)
- `disaster_type`: Type of disaster (e.g., "earthquake", "flood", "wildfire", "hurricane", "tsunami", "volcanic_eruption", "cyclone")
- `title`: Disaster event title/headline
- `description`: Detailed description
- `latitude`: Latitude coordinate (decimal degrees)
- `longitude`: Longitude coordinate (decimal degrees)
- `geom`: PostGIS POINT geometry (SRID 4326)
- `occurred_at`: Date and time when disaster occurred
- `magnitude`: Magnitude/severity value (e.g., Richter scale for earthquakes)
- `severity`: Severity category (e.g., "low", "medium", "high", "critical")
- `status`: Status (e.g., "active", "resolved", "ongoing")
- `source`: Data source name (e.g., "USGS", "NOAA", "ReliefWeb")
- `source_id`: Unique identifier from source API
- `url`: URL to detailed information
- `affected_area`: PostGIS POLYGON geometry for affected area (optional)
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp
- `data_fetched_at`: Timestamp when data was fetched from external API

**Constraints:**
- `disaster_type` and `occurred_at` are required
- `latitude` and `longitude` are required
- Unique constraint on (source, source_id) to prevent duplicates

**Disaster Types:**
- earthquake
- flood
- wildfire
- hurricane
- cyclone
- tsunami
- volcanic_eruption
- tornado
- drought
- landslide
- storm
- other

---

#### 6.3.3 AQI Measurements Table

**Table Name:** `aqi_measurements`

**Purpose:** Store Air Quality Index measurements with individual pollutant values.

**Schema:**

```sql
CREATE TABLE aqi_measurements (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    city_name VARCHAR(255),  -- Denormalized for performance
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    geom GEOMETRY(POINT, 4326),  -- PostGIS point geometry
    measured_at TIMESTAMP NOT NULL,
    aqi_value INTEGER,  -- Overall AQI value (0-500)
    aqi_category VARCHAR(50),  -- good, moderate, unhealthy, etc.
    pm25 DECIMAL(8, 2),  -- PM2.5 value (µg/m³)
    pm10 DECIMAL(8, 2),  -- PM10 value (µg/m³)
    o3 DECIMAL(8, 2),  -- Ozone value (ppb or µg/m³)
    no2 DECIMAL(8, 2),  -- Nitrogen Dioxide value (ppb or µg/m³)
    co DECIMAL(8, 2),  -- Carbon Monoxide value (ppm or µg/m³)
    so2 DECIMAL(8, 2),  -- Sulfur Dioxide value (ppb or µg/m³)
    source VARCHAR(255),  -- API source name
    source_id VARCHAR(255),  -- External API ID
    url TEXT,  -- Link to detailed information
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fetched_at TIMESTAMP  -- When data was fetched from API
);

-- Create spatial index on point geometry
CREATE INDEX idx_aqi_measurements_geom ON aqi_measurements USING GIST (geom);

-- Create indexes for common queries
CREATE INDEX idx_aqi_measurements_city_id ON aqi_measurements (city_id);
CREATE INDEX idx_aqi_measurements_measured_at ON aqi_measurements (measured_at);
CREATE INDEX idx_aqi_measurements_city_date ON aqi_measurements (city_id, measured_at);
CREATE INDEX idx_aqi_measurements_aqi_value ON aqi_measurements (aqi_value);

-- Composite index for time series queries
CREATE INDEX idx_aqi_measurements_city_time ON aqi_measurements (city_id, measured_at DESC);
```

**Fields:**
- `id`: Primary key (auto-increment)
- `city_id`: Foreign key to cities table (optional, if city is in cities table)
- `city_name`: City name (denormalized for faster queries)
- `latitude`: Latitude coordinate (decimal degrees)
- `longitude`: Longitude coordinate (decimal degrees)
- `geom`: PostGIS POINT geometry (SRID 4326)
- `measured_at`: Date and time when measurement was taken
- `aqi_value`: Overall AQI value (0-500)
- `aqi_category`: AQI category (e.g., "good", "moderate", "unhealthy_for_sensitive_groups", "unhealthy", "very_unhealthy", "hazardous")
- `pm25`: PM2.5 particulate matter concentration (µg/m³)
- `pm10`: PM10 particulate matter concentration (µg/m³)
- `o3`: Ozone concentration (ppb or µg/m³)
- `no2`: Nitrogen Dioxide concentration (ppb or µg/m³)
- `co`: Carbon Monoxide concentration (ppm or µg/m³)
- `so2`: Sulfur Dioxide concentration (ppb or µg/m³)
- `source`: Data source name (e.g., "OpenAQ", "AQICN")
- `source_id`: Unique identifier from source API
- `url`: URL to detailed information
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp
- `data_fetched_at`: Timestamp when data was fetched from external API

**Constraints:**
- `measured_at` is required
- `latitude` and `longitude` are required
- At least one pollutant value (pm25, pm10, o3, no2, co, so2) should be present
- AQI category should match AQI value range

**AQI Categories:**
- good (0-50)
- moderate (51-100)
- unhealthy_for_sensitive_groups (101-150)
- unhealthy (151-200)
- very_unhealthy (201-300)
- hazardous (301-500)

---

### 6.4 Spatial Data Structure

**6.4.1 Coordinate Reference System (CRS)**

All spatial data in the database uses:
- **SRID:** 4326 (WGS84 - World Geodetic System 1984)
- **Projection:** Geographic (latitude/longitude)
- **Unit:** Decimal degrees

**6.4.2 Spatial Data Types**

1. **POINT Geometry:**
   - Used for: City locations, disaster locations, AQI measurement locations
   - Storage: Coordinates as (longitude, latitude) in WGS84

2. **POLYGON Geometry (Optional):**
   - Used for: City boundaries, affected disaster areas
   - Storage: Polygon coordinates in WGS84

**6.4.3 Spatial Indexing**

- **GIST Indexes:** Created on all geometry columns for efficient spatial queries
- **Spatial Functions:** PostGIS functions used for spatial operations:
  - `ST_Distance` - Calculate distance between geometries
  - `ST_Within` - Check if point is within polygon
  - `ST_Intersects` - Check if geometries intersect
  - `ST_Buffer` - Create buffer around geometry
  - `ST_Transform` - Transform coordinates (if needed)
  - `ST_GeomFromText` - Create geometry from WKT text
  - `ST_AsGeoJSON` - Convert geometry to GeoJSON

---

### 6.5 Database Functions and Views (Optional)

**6.5.1 Materialized Views (Optional)**

For performance optimization, materialized views can be created:

```sql
-- Latest AQI measurements per city
CREATE MATERIALIZED VIEW latest_aqi_per_city AS
SELECT DISTINCT ON (city_id)
    id, city_id, city_name, latitude, longitude, geom,
    measured_at, aqi_value, aqi_category,
    pm25, pm10, o3, no2, co, so2
FROM aqi_measurements
ORDER BY city_id, measured_at DESC;

CREATE INDEX idx_latest_aqi_city_id ON latest_aqi_per_city (city_id);

-- Refresh materialized view periodically
-- REFRESH MATERIALIZED VIEW latest_aqi_per_city;
```

**6.5.2 Helper Functions (Optional)**

```sql
-- Function to calculate distance between two points
CREATE OR REPLACE FUNCTION distance_between_points(
    lat1 DECIMAL, lon1 DECIMAL,
    lat2 DECIMAL, lon2 DECIMAL
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN ST_Distance(
        ST_MakePoint(lon1, lat1)::geography,
        ST_MakePoint(lon2, lat2)::geography
    );
END;
$$ LANGUAGE plpgsql;

-- Function to find nearest city to coordinates
CREATE OR REPLACE FUNCTION find_nearest_city(
    lat DECIMAL, lon DECIMAL
)
RETURNS TABLE(city_id INTEGER, city_name VARCHAR, distance DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        ST_Distance(
            ST_MakePoint(lon, lat)::geography,
            c.geom::geography
        ) AS distance
    FROM cities c
    ORDER BY distance
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

---

### 6.6 GeoServer Layer Configuration

**6.6.1 GeoServer Workspace**

- **Workspace Name:** `disaster_aqi` (or custom name)
- **Namespace URI:** `http://localhost:8080/disaster_aqi`

**6.6.2 Data Store Configuration**

- **Data Store Name:** `postgis_store`
- **Type:** PostGIS
- **Connection Parameters:**
  - Host: `localhost` (or database host)
  - Port: `5432` (PostgreSQL default port)
  - Database: `disaster_aqi_db` (or database name)
  - Schema: `public`
  - User: Database username
  - Password: Database password
  - Validate connections: Yes

**6.6.3 Layer Configuration (Minimum One Required)**

**Layer 1: Cities Layer**

- **Layer Name:** `cities`
- **Native SRS:** EPSG:4326
- **Declared SRS:** EPSG:4326
- **Type:** Vector (point geometry)
- **Feature Type:** Point
- **Style:** Custom SLD (Styled Layer Descriptor) for city markers
- **Publishing:**
  - WMS enabled: Yes
  - WFS enabled: Yes (optional)
  - Feature Caching: Enabled (optional)

**Alternative/Additional Layers:**

- **Disasters Layer:** Vector layer for disaster events
- **AQI Measurements Layer:** Vector layer for AQI data points
- **City Boundaries Layer:** Polygon layer for city boundaries (if available)

**6.6.4 Style Configuration**

GeoServer layers require SLD (Styled Layer Descriptor) files for symbology:

- **Cities Style:** Simple point markers or custom icons
- **Disasters Style:** Different symbols/icons for different disaster types
- **AQI Style:** Color-coded points based on AQI values

**6.6.5 Layer Publishing**

Layers are published as:
- **WMS (Web Map Service):** For map tile rendering
- **WFS (Web Feature Service):** For vector data access (optional)

**WMS Capabilities:**
- Image format: PNG, JPEG
- CRS: EPSG:4326, EPSG:3857 (Web Mercator)
- Output format: image/png, image/jpeg

---

### 6.7 Database Initialization

**6.7.1 Database Setup Steps**

1. Create PostgreSQL database
2. Enable PostGIS extension
3. Create tables (using schema definitions above)
4. Create indexes
5. Create functions/views (optional)
6. Configure GeoServer data store
7. Publish GeoServer layers

**6.7.2 Sample SQL Script**

```sql
-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create tables (use schema definitions from 6.3)

-- Insert sample cities (example)
INSERT INTO cities (name, country, country_code, latitude, longitude, geom)
VALUES 
    ('New York', 'United States', 'US', 40.7128, -74.0060, 
     ST_SetSRID(ST_MakePoint(-74.0060, 40.7128), 4326)),
    ('London', 'United Kingdom', 'GB', 51.5074, -0.1278,
     ST_SetSRID(ST_MakePoint(-0.1278, 51.5074), 4326));

-- (Continue with schema setup...)
```

---

### 6.8 Data Maintenance

**6.8.1 Data Updates**

- Disaster data: Fetched periodically from external APIs (every 10 minutes)
- AQI data: Fetched periodically from external APIs (every 15 minutes)
- Historical data: Stored with timestamps for tracking

**6.8.2 Data Retention**

- Historical disaster data: 1 year (as per requirement)
- Historical AQI data: 1 year (as per requirement)
- Older data can be archived or deleted (optional)

**6.8.3 Database Maintenance**

- Regular VACUUM and ANALYZE operations
- Index maintenance
- Backup strategy (recommended)
- Connection pooling for performance

---

### 6.9 Performance Considerations

**6.9.1 Indexing Strategy**

- Spatial indexes (GIST) on all geometry columns
- B-tree indexes on frequently queried columns (date, type, city_id)
- Composite indexes for common query patterns

**6.9.2 Query Optimization**

- Use spatial indexes for spatial queries
- Limit result sets with WHERE clauses
- Use EXPLAIN ANALYZE to optimize queries
- Consider materialized views for frequently accessed aggregations

**6.9.3 Connection Pooling**

- Use connection pooling (e.g., SQLAlchemy pool) to manage database connections
- Configure appropriate pool size based on expected load

---

This completes the database design section. The database schema provides a solid foundation for storing and querying spatial disaster and AQI data efficiently using PostGIS.
