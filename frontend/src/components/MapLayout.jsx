import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Tooltip, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

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

const MapUpdater = ({ startPoint, endPoint, selectedRoute }) => {
  const map = useMap();
  
  useEffect(() => {
    if (selectedRoute && selectedRoute.path && selectedRoute.path.length > 0) {
      const bounds = L.latLngBounds(selectedRoute.path);
      map.fitBounds(bounds, { padding: [50, 50] });
    } else if (startPoint && endPoint) {
      const bounds = L.latLngBounds([startPoint, endPoint]);
      map.fitBounds(bounds, { padding: [50, 50] });
    } else if (startPoint) {
      map.flyTo(startPoint, 13);
    }
  }, [startPoint, endPoint, selectedRoute, map]);
  
  return null;
};

const MapLayout = ({ startPoint, endPoint, activeRoutes = [], selectedIndex = 0 }) => {
  const defaultCenter = [30.3165, 78.0322];
  const center = startPoint || defaultCenter;

  return (
    <div className="absolute inset-0 z-0">
      <MapContainer 
        center={center} 
        zoom={13} 
        zoomControl={false}
        className="w-full h-full"
        style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, zIndex: 1 }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapUpdater 
          startPoint={startPoint} 
          endPoint={endPoint} 
          selectedRoute={activeRoutes[selectedIndex]} 
        />
        
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

        {activeRoutes.map((route, index) => {
          const isSelected = index === selectedIndex;
          const color = isSelected ? '#3b82f6' : route.color;
          const weight = isSelected ? 8 : 4;
          const opacity = isSelected ? 1 : 0.5;
          
          return (
            <Polyline 
              key={index} 
              positions={route.path} 
              color={color} 
              weight={weight} 
              opacity={opacity} 
            >
              <Tooltip sticky>{route.type} ({ (route.total_distance / 1000).toFixed(1) } km)</Tooltip>
            </Polyline>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default MapLayout;
