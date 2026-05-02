import React, { useState } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import MapLayout from './components/MapLayout';
import './App.css';

function App() {
  const [activeRoutes, setActiveRoutes] = useState([]);
  const [startPoint, setStartPoint] = useState(null);
  const [endPoint, setEndPoint] = useState(null);

  const handleRouteCompute = async (start, destination) => {
    console.log("Computing route from", start, "to", destination);
    
    try {
      // Geocode start location
      const startRes = await axios.get('https://nominatim.openstreetmap.org/search', {
        params: { q: start, format: 'json', limit: 1 }
      });
      
      // Geocode end location
      const endRes = await axios.get('https://nominatim.openstreetmap.org/search', {
        params: { q: destination, format: 'json', limit: 1 }
      });

      if (startRes.data.length > 0 && endRes.data.length > 0) {
        const startCoords = [parseFloat(startRes.data[0].lat), parseFloat(startRes.data[0].lon)];
        const endCoords = [parseFloat(endRes.data[0].lat), parseFloat(endRes.data[0].lon)];
        
        setStartPoint(startCoords);
        setEndPoint(endCoords);

        // Calculate a simple midpoint for the mock curved routes
        const midLat = (startCoords[0] + endCoords[0]) / 2;
        const midLon = (startCoords[1] + endCoords[1]) / 2;

        // Mock Route Lines between the actual points
        setActiveRoutes([
          {
            color: '#10b981', // Safest - Teal
            coordinates: [
              startCoords,
              [midLat + 0.005, midLon - 0.005], // Slight curve
              endCoords
            ]
          },
          {
            color: '#ef4444', // Shortest - Red
            coordinates: [
              startCoords,
              [midLat - 0.002, midLon + 0.002], // Slight curve
              endCoords
            ]
          }
        ]);
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
      <Sidebar onRouteCompute={handleRouteCompute} />
      <MapLayout 
        startPoint={startPoint} 
        endPoint={endPoint} 
        activeRoutes={activeRoutes} 
      />
    </div>
  );
}

export default App;
