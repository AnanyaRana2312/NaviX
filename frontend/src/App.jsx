import React, { useState } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import MapLayout from './components/MapLayout';
import './App.css';
import { fetchRoutes } from './api/routes';

function App() {
  const [activeRoutes, setActiveRoutes] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [startPoint, setStartPoint] = useState(null);
  const [endPoint, setEndPoint] = useState(null);

  const handleRouteCompute = async (start, destination) => {
    try {
      const startRes = await axios.get('https://nominatim.openstreetmap.org/search', {
        params: { q: start, format: 'json', limit: 1 }
      });
      const endRes = await axios.get('https://nominatim.openstreetmap.org/search', {
        params: { q: destination, format: 'json', limit: 1 }
      });

      if (startRes.data.length > 0 && endRes.data.length > 0) {
        const startCoords = [parseFloat(startRes.data[0].lat), parseFloat(startRes.data[0].lon)];
        const endCoords = [parseFloat(endRes.data[0].lat), parseFloat(endRes.data[0].lon)];
        
        setStartPoint(startCoords);
        setEndPoint(endCoords);

        try {
          const routeData = await fetchRoutes(startCoords, endCoords, destination);
          if (routeData && routeData.routes) {
            const mappedRoutes = routeData.routes.map((r, idx) => ({
              ...r,
              id: idx,
              type: idx === 0 ? "Safest Route" : (idx === routeData.routes.length - 1 ? "Shortest Route" : "Balanced Route"),
              color: idx === 0 ? '#10b981' : (idx === routeData.routes.length - 1 ? '#ef4444' : '#f59e0b')
            }));
            setActiveRoutes(mappedRoutes);
            setSelectedIndex(0);
          }
        } catch (apiError) {
          console.error("Backend API error:", apiError);
          alert("Failed to compute routes. Is the backend running?");
        }
      } else {
        alert("Could not find one or both locations. Please try again.");
      }
    } catch (error) {
      console.error("Geocoding error:", error);
      alert("Failed to geocode locations.");
    }
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-slate-900">
      <Sidebar 
        onRouteCompute={handleRouteCompute} 
        routes={activeRoutes}
        selectedIndex={selectedIndex}
        onSelectRoute={setSelectedIndex}
      />
      <MapLayout 
        startPoint={startPoint} 
        endPoint={endPoint} 
        activeRoutes={activeRoutes} 
        selectedIndex={selectedIndex}
      />
    </div>
  );
}

export default App;
