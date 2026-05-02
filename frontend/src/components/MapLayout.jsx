import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet with Vite
import L from 'leaflet';
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl,
  iconUrl,
  shadowUrl,
});

// Component to dynamically re-center map
const MapUpdater = ({ startPoint, endPoint }) => {
  const map = useMap();
  
  useEffect(() => {
    if (startPoint && endPoint) {
      const bounds = L.latLngBounds([startPoint, endPoint]);
      map.fitBounds(bounds, { padding: [50, 50] });
    } else if (startPoint) {
      map.flyTo(startPoint, 13);
    }
  }, [startPoint, endPoint, map]);
  
  return null;
};

const MapLayout = ({ startPoint, endPoint, activeRoutes = [] }) => {
  // Default to a central city coordinate (e.g., New York for demo) if no points
  const defaultCenter = [40.7128, -74.0060];
  const center = startPoint || defaultCenter;

  return (
    <div className="absolute inset-0 z-0">
      <MapContainer 
        center={center} 
        zoom={13} 
        zoomControl={false}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        <MapUpdater startPoint={startPoint} endPoint={endPoint} />
        
        {startPoint && (
          <Marker position={startPoint}>
            <Popup>Start Location</Popup>
          </Marker>
        )}
        
        {endPoint && (
          <Marker position={endPoint}>
            <Popup>Destination</Popup>
          </Marker>
        )}

        {/* Render Routes - This will be populated once API is hooked up */}
        {activeRoutes.map((route, index) => (
          <Polyline 
            key={index} 
            positions={route.coordinates} 
            color={route.color} 
            weight={5} 
            opacity={0.8} 
          />
        ))}
      </MapContainer>
    </div>
  );
};

export default MapLayout;
