import React, { useEffect, useState } from 'react';
import { MapContainer as LeafletMapContainer, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import DisasterLayer from '../Layers/DisasterLayer';
import AQILayer from '../Layers/AQILayer';
import { useFilters } from '../../context/FilterContext';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in React-Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

L.Marker.prototype.options.icon = DefaultIcon;

const MapContainer: React.FC = () => {
  const [mapInstance, setMapInstance] = useState<L.Map | null>(null);

  return (
    <div className="w-full h-full relative">
      <LeafletMapContainer
        center={[20, 0]}
        zoom={2}
        style={{ height: '100%', width: '100%' }}
        whenCreated={setMapInstance}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <DisasterLayer />
        <AQILayer />
        
        <MapController />
      </LeafletMapContainer>
    </div>
  );
};

// Component to control map view
const MapController: React.FC = () => {
  const map = useMap();

  useEffect(() => {
    // Any map initialization logic
  }, [map]);

  return null;
};

export default MapContainer;
