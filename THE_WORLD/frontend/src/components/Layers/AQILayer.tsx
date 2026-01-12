import React, { useEffect, useState } from 'react';
import { useMap, Marker, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import { aqiAPI } from '../../services/api';
import { AQIMeasurement } from '../../types';
import { useFilters } from '../../context/FilterContext';

const AQILayer: React.FC = () => {
  const [aqiData, setAqiData] = useState<AQIMeasurement[]>([]);
  const [loading, setLoading] = useState(false);
  const [visible, setVisible] = useState(true);
  const { filters } = useFilters();
  const map = useMap();

  useEffect(() => {
    fetchAQI();
  }, [filters]);

  const fetchAQI = async () => {
    setLoading(true);
    try {
      const params: any = {};
      
      if (filters.citySearch) {
        params.city_name = filters.citySearch;
      }
      
      if (filters.aqiRange.min !== null) {
        params.min_aqi = filters.aqiRange.min;
      }
      
      if (filters.aqiRange.max !== null) {
        params.max_aqi = filters.aqiRange.max;
      }

      const response = await aqiAPI.getLatest(params);
      
      if (response.success && response.data) {
        setAqiData(response.data);
      }
    } catch (error) {
      console.error('Error fetching AQI data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAQIColor = (aqi: number | null) => {
    if (!aqi) return '#999999';
    
    if (aqi <= 50) return '#00E400';      // Good - Green
    if (aqi <= 100) return '#FFFF00';     // Moderate - Yellow
    if (aqi <= 150) return '#FF7E00';     // Unhealthy for Sensitive - Orange
    if (aqi <= 200) return '#FF0000';     // Unhealthy - Red
    if (aqi <= 300) return '#8F3F97';     // Very Unhealthy - Purple
    return '#7E0023';                      // Hazardous - Maroon
  };

  const getAQICategory = (aqi: number | null) => {
    if (!aqi) return 'Unknown';
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Moderate';
    if (aqi <= 150) return 'Unhealthy for Sensitive Groups';
    if (aqi <= 200) return 'Unhealthy';
    if (aqi <= 300) return 'Very Unhealthy';
    return 'Hazardous';
  };

  const getAQIIcon = (aqi: number | null) => {
    const color = getAQIColor(aqi);
    const size = aqi && aqi > 150 ? 16 : 12;

    return L.divIcon({
      className: 'custom-aqi-marker',
      html: `<div style="
        width: ${size}px;
        height: ${size}px;
        background-color: ${color};
        border: 2px solid white;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      "></div>`,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
    });
  };

  const getAQIPopupContent = (measurement: AQIMeasurement) => {
    const category = getAQICategory(measurement.aqi_value);
    return `
      <div style="min-width: 220px;">
        <h3 style="margin: 0 0 8px 0; font-weight: bold; color: #333;">
          ${measurement.city_name || 'Unknown City'}
        </h3>
        <div style="margin-bottom: 8px;">
          <span style="
            display: inline-block;
            padding: 4px 12px;
            background-color: ${getAQIColor(measurement.aqi_value)};
            color: white;
            border-radius: 4px;
            font-weight: bold;
          ">
            AQI: ${measurement.aqi_value || 'N/A'} - ${category}
          </span>
        </div>
        <div style="font-size: 13px;">
          ${measurement.pm25 ? `<p style="margin: 2px 0;">PM2.5: ${measurement.pm25.toFixed(1)} µg/m³</p>` : ''}
          ${measurement.pm10 ? `<p style="margin: 2px 0;">PM10: ${measurement.pm10.toFixed(1)} µg/m³</p>` : ''}
          ${measurement.o3 ? `<p style="margin: 2px 0;">O₃: ${measurement.o3.toFixed(1)} ppb</p>` : ''}
          ${measurement.no2 ? `<p style="margin: 2px 0;">NO₂: ${measurement.no2.toFixed(1)} ppb</p>` : ''}
          ${measurement.co ? `<p style="margin: 2px 0;">CO: ${measurement.co.toFixed(1)} ppm</p>` : ''}
          ${measurement.so2 ? `<p style="margin: 2px 0;">SO₂: ${measurement.so2.toFixed(1)} ppb</p>` : ''}
        </div>
        <p style="margin: 8px 0 0 0; font-size: 11px; color: #999;">
          ${new Date(measurement.measured_at).toLocaleString()}
        </p>
      </div>
    `;
  };

  if (!visible) return null;

  if (loading) {
    return (
      <div className="absolute top-4 right-4 bg-white px-4 py-2 rounded shadow-lg z-[1000]">
        <span className="text-sm">Loading AQI data...</span>
      </div>
    );
  }

  return (
    <>
      {aqiData.map((measurement) => (
        <Marker
          key={measurement.id}
          position={[measurement.latitude, measurement.longitude]}
          icon={getAQIIcon(measurement.aqi_value)}
        >
          <Popup>
            <div dangerouslySetInnerHTML={{ __html: getAQIPopupContent(measurement) }} />
          </Popup>
        </Marker>
      ))}
    </>
  );
};

export default AQILayer;
