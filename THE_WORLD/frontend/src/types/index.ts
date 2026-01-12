/**
 * THE_WORLD - Type Definitions
 */

export interface Disaster {
  id: number;
  disaster_type: string;
  title: string | null;
  description: string | null;
  latitude: number;
  longitude: number;
  occurred_at: string;
  magnitude: number | null;
  severity: string | null;
  status: string | null;
  source: string | null;
  source_id: string | null;
  url: string | null;
}

export interface AQIMeasurement {
  id: number;
  city_id: number | null;
  city_name: string | null;
  latitude: number;
  longitude: number;
  measured_at: string;
  aqi_value: number | null;
  aqi_category: string | null;
  pm25: number | null;
  pm10: number | null;
  o3: number | null;
  no2: number | null;
  co: number | null;
  so2: number | null;
  source: string | null;
  url: string | null;
}

export interface City {
  id: number;
  name: string;
  country: string;
  country_code: string | null;
  latitude: number;
  longitude: number;
  population: number | null;
  timezone: string | null;
}

export interface GeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number];
  };
  properties: any;
}

export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}
