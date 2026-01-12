import React, { useEffect, useState } from 'react';
import { useMap, Marker, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import { disastersAPI } from '../../services/api';
import { Disaster, GeoJSONFeatureCollection } from '../../types';
import { useFilters } from '../../context/FilterContext';

const DisasterLayer: React.FC = () => {
  const [disasters, setDisasters] = useState<Disaster[]>([]);
  const [loading, setLoading] = useState(false);
  const { filters } = useFilters();
  const map = useMap();

  useEffect(() => {
    fetchDisasters();
  }, [filters]);

  const fetchDisasters = async () => {
    setLoading(true);
    try {
      const params: any = {};
      
      if (filters.disasterType.length > 0) {
        params.disaster_type = filters.disasterType[0]; // API supports one type at a time
      }
      
      if (filters.dateRange.start) {
        params.start_date = filters.dateRange.start;
      }
      
      if (filters.dateRange.end) {
        params.end_date = filters.dateRange.end;
      }

      const response = await disastersAPI.getAll(params);
      
      if (response.success && response.data) {
        setDisasters(response.data);
      }
    } catch (error) {
      console.error('Error fetching disasters:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDisasterIcon = (disasterType: string, severity?: string | null) => {
    const colors: Record<string, string> = {
      earthquake: '#FF0000',
      flood: '#0066FF',
      wildfire: '#FF6600',
      hurricane: '#9900FF',
      cyclone: '#9900FF',
      tornado: '#FF0066',
      storm: '#00CCFF',
      default: '#888888',
    };

    const color = colors[disasterType] || colors.default;

    return L.divIcon({
      className: 'custom-disaster-marker',
      html: `<div style="
        width: 12px;
        height: 12px;
        background-color: ${color};
        border: 2px solid white;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      "></div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6],
    });
  };

  const getDisasterLabel = (disaster: Disaster) => {
    return `
      <div style="min-width: 200px;">
        <h3 style="margin: 0 0 8px 0; font-weight: bold; color: #333;">
          ${disaster.disaster_type.charAt(0).toUpperCase() + disaster.disaster_type.slice(1)}
        </h3>
        ${disaster.title ? `<p style="margin: 0 0 4px 0; color: #666;">${disaster.title}</p>` : ''}
        ${disaster.magnitude ? `<p style="margin: 0 0 4px 0;">Magnitude: ${disaster.magnitude}</p>` : ''}
        <p style="margin: 0 0 4px 0; font-size: 12px; color: #999;">
          ${new Date(disaster.occurred_at).toLocaleString()}
        </p>
        ${disaster.source ? `<p style="margin: 0; font-size: 11px; color: #999;">Source: ${disaster.source}</p>` : ''}
      </div>
    `;
  };

  if (loading) {
    return (
      <div className="absolute top-4 left-4 bg-white px-4 py-2 rounded shadow-lg z-[1000]">
        <span className="text-sm">Loading disasters...</span>
      </div>
    );
  }

  return (
    <>
      {disasters.map((disaster) => (
        <Marker
          key={disaster.id}
          position={[disaster.latitude, disaster.longitude]}
          icon={getDisasterIcon(disaster.disaster_type, disaster.severity)}
        >
          <Popup>
            <div dangerouslySetInnerHTML={{ __html: getDisasterLabel(disaster) }} />
          </Popup>
        </Marker>
      ))}
    </>
  );
};

export default DisasterLayer;
