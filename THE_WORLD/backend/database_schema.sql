-- THE_WORLD - WebGIS Disaster and AQI Monitoring System
-- Database Schema for PostgreSQL with PostGIS Extension
-- Database: WebGis

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================
-- CITIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    country_code VARCHAR(2),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    geom GEOMETRY(POINT, 4326),
    boundary GEOMETRY(POLYGON, 4326),
    population INTEGER,
    timezone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index on point geometry
CREATE INDEX IF NOT EXISTS idx_cities_geom ON cities USING GIST (geom);

-- Create spatial index on boundary polygon
CREATE INDEX IF NOT EXISTS idx_cities_boundary ON cities USING GIST (boundary);

-- Create indexes for faster searches
CREATE INDEX IF NOT EXISTS idx_cities_name ON cities (name);
CREATE INDEX IF NOT EXISTS idx_cities_country ON cities (country);
CREATE INDEX IF NOT EXISTS idx_cities_country_code ON cities (country_code);

-- ============================================
-- DISASTERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS disasters (
    id SERIAL PRIMARY KEY,
    disaster_type VARCHAR(50) NOT NULL,
    title VARCHAR(500),
    description TEXT,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    geom GEOMETRY(POINT, 4326),
    occurred_at TIMESTAMP NOT NULL,
    magnitude DECIMAL(10, 2),
    severity VARCHAR(50),
    status VARCHAR(50),
    source VARCHAR(255),
    source_id VARCHAR(255),
    url TEXT,
    affected_area GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fetched_at TIMESTAMP,
    
    -- Unique constraint to prevent duplicates
    CONSTRAINT unique_disaster_source UNIQUE (source, source_id)
);

-- Create spatial index on point geometry
CREATE INDEX IF NOT EXISTS idx_disasters_geom ON disasters USING GIST (geom);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_disasters_type ON disasters (disaster_type);
CREATE INDEX IF NOT EXISTS idx_disasters_occurred_at ON disasters (occurred_at);
CREATE INDEX IF NOT EXISTS idx_disasters_source_id ON disasters (source, source_id);
CREATE INDEX IF NOT EXISTS idx_disasters_status ON disasters (status);
CREATE INDEX IF NOT EXISTS idx_disasters_type_date ON disasters (disaster_type, occurred_at);

-- ============================================
-- AQI MEASUREMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS aqi_measurements (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE SET NULL,
    city_name VARCHAR(255),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    geom GEOMETRY(POINT, 4326),
    measured_at TIMESTAMP NOT NULL,
    aqi_value INTEGER,
    aqi_category VARCHAR(50),
    pm25 DECIMAL(8, 2),
    pm10 DECIMAL(8, 2),
    o3 DECIMAL(8, 2),
    no2 DECIMAL(8, 2),
    co DECIMAL(8, 2),
    so2 DECIMAL(8, 2),
    source VARCHAR(255),
    source_id VARCHAR(255),
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fetched_at TIMESTAMP
);

-- Create spatial index on point geometry
CREATE INDEX IF NOT EXISTS idx_aqi_measurements_geom ON aqi_measurements USING GIST (geom);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_aqi_measurements_city_id ON aqi_measurements (city_id);
CREATE INDEX IF NOT EXISTS idx_aqi_measurements_measured_at ON aqi_measurements (measured_at);
CREATE INDEX IF NOT EXISTS idx_aqi_measurements_city_date ON aqi_measurements (city_id, measured_at);
CREATE INDEX IF NOT EXISTS idx_aqi_measurements_aqi_value ON aqi_measurements (aqi_value);
CREATE INDEX IF NOT EXISTS idx_aqi_measurements_city_time ON aqi_measurements (city_id, measured_at DESC);
CREATE INDEX IF NOT EXISTS idx_aqi_measurements_city_name ON aqi_measurements (city_name);

-- ============================================
-- FUNCTION: Update updated_at timestamp
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_cities_updated_at BEFORE UPDATE ON cities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_disasters_updated_at BEFORE UPDATE ON disasters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_aqi_measurements_updated_at BEFORE UPDATE ON aqi_measurements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- FUNCTION: Calculate AQI Category
-- ============================================
CREATE OR REPLACE FUNCTION calculate_aqi_category(aqi_value INTEGER)
RETURNS VARCHAR(50) AS $$
BEGIN
    IF aqi_value <= 50 THEN
        RETURN 'good';
    ELSIF aqi_value <= 100 THEN
        RETURN 'moderate';
    ELSIF aqi_value <= 150 THEN
        RETURN 'unhealthy_for_sensitive_groups';
    ELSIF aqi_value <= 200 THEN
        RETURN 'unhealthy';
    ELSIF aqi_value <= 300 THEN
        RETURN 'very_unhealthy';
    ELSE
        RETURN 'hazardous';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================
-- Uncomment to insert sample cities
/*
INSERT INTO cities (name, country, country_code, latitude, longitude, geom)
VALUES 
    ('New York', 'United States', 'US', 40.7128, -74.0060, 
     ST_SetSRID(ST_MakePoint(-74.0060, 40.7128), 4326)),
    ('London', 'United Kingdom', 'GB', 51.5074, -0.1278,
     ST_SetSRID(ST_MakePoint(-0.1278, 51.5074), 4326)),
    ('Tokyo', 'Japan', 'JP', 35.6762, 139.6503,
     ST_SetSRID(ST_MakePoint(139.6503, 35.6762), 4326)),
    ('Paris', 'France', 'FR', 48.8566, 2.3522,
     ST_SetSRID(ST_MakePoint(2.3522, 48.8566), 4326)),
    ('Sydney', 'Australia', 'AU', -33.8688, 151.2093,
     ST_SetSRID(ST_MakePoint(151.2093, -33.8688), 4326))
ON CONFLICT DO NOTHING;
*/
