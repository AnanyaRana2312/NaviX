import React, { useState, useMemo } from 'react';
import { Search, Navigation, ShieldCheck, MapPin, Route as RouteIcon, Info } from 'lucide-react';

const getBearing = (lat1, lon1, lat2, lon2) => {
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const l1 = lat1 * Math.PI / 180;
  const l2 = lat2 * Math.PI / 180;
  const y = Math.sin(dLon) * Math.cos(l2);
  const x = Math.cos(l1) * Math.sin(l2) - Math.sin(l1) * Math.cos(l2) * Math.cos(dLon);
  return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
};

const getTurn = (bearing1, bearing2) => {
  let diff = (bearing2 - bearing1 + 360) % 360;
  if (diff > 180) diff -= 360;
  if (diff > 30 && diff <= 150) return "Turn Right";
  if (diff < -30 && diff >= -150) return "Turn Left";
  if (Math.abs(diff) > 150) return "U-Turn";
  return "Go Straight";
};

const distanceMeters = (lat1, lon1, lat2, lon2) => {
  const R = 6371e3;
  const p1 = lat1 * Math.PI/180;
  const p2 = lat2 * Math.PI/180;
  const dp = (lat2-lat1) * Math.PI/180;
  const dl = (lon2-lon1) * Math.PI/180;
  const a = Math.sin(dp/2) * Math.sin(dp/2) + Math.cos(p1) * Math.cos(p2) * Math.sin(dl/2) * Math.sin(dl/2);
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
};

const generateTurnByTurn = (path) => {
  if (!path || path.length < 3) return ["Proceed to destination."];
  const steps = [];
  let accumulatedDistance = 0;
  
  let simplifiedPath = [path[0]];
  for (let i = 1; i < path.length; i++) {
    const d = distanceMeters(
      simplifiedPath[simplifiedPath.length-1][0], 
      simplifiedPath[simplifiedPath.length-1][1], 
      path[i][0], 
      path[i][1]
    );
    if (d > 20 || i === path.length - 1) { 
      simplifiedPath.push(path[i]);
    }
  }

  for (let i = 0; i < simplifiedPath.length - 2; i++) {
    const p1 = simplifiedPath[i];
    const p2 = simplifiedPath[i+1];
    const p3 = simplifiedPath[i+2];
    
    accumulatedDistance += distanceMeters(p1[0], p1[1], p2[0], p2[1]);
    const b1 = getBearing(p1[0], p1[1], p2[0], p2[1]);
    const b2 = getBearing(p2[0], p2[1], p3[0], p3[1]);
    const turn = getTurn(b1, b2);
    
    if (turn !== "Go Straight") {
      steps.push(`${turn} after ${Math.round(accumulatedDistance)}m`);
      accumulatedDistance = 0;
    }
  }
  
  accumulatedDistance += distanceMeters(
    simplifiedPath[simplifiedPath.length-2][0], simplifiedPath[simplifiedPath.length-2][1], 
    simplifiedPath[simplifiedPath.length-1][0], simplifiedPath[simplifiedPath.length-1][1]
  );
  if (accumulatedDistance > 0) {
    steps.push(`Arrive at destination in ${Math.round(accumulatedDistance)}m`);
  }
  return steps;
};

const Sidebar = ({ onRouteCompute, routes = [], selectedIndex = 0, onSelectRoute }) => {
  const [start, setStart] = useState('');
  const [destination, setDestination] = useState('');

  const handleCompute = (e) => {
    e.preventDefault();
    if (onRouteCompute) {
      onRouteCompute(start, destination);
    }
  };

  const selectedRoute = routes[selectedIndex];
  const turnInstructions = useMemo(() => {
    if (!selectedRoute || !selectedRoute.path) return [];
    return generateTurnByTurn(selectedRoute.path);
  }, [selectedRoute]);

  return (
    <div className="absolute top-4 left-4 z-10 w-96 flex flex-col gap-4 max-h-[95vh]">
      {/* Brand Header */}
      <div className="glass-panel rounded-2xl p-6 flex items-center gap-4 shadow-xl">
        <div className="bg-gradient-to-br from-blue-500 to-teal-400 p-3 rounded-xl shadow-lg shadow-blue-500/20">
          <Navigation className="w-8 h-8 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-teal-300">
            NaviX
          </h1>
          <p className="text-sm text-slate-400 font-medium tracking-wide">Safety-Aware Routing</p>
        </div>
      </div>

      {/* Input Panel */}
      <div className="glass-panel rounded-2xl p-6 flex flex-col gap-5 shadow-xl">
        <form onSubmit={handleCompute} className="flex flex-col gap-4">
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MapPin className="h-5 w-5 text-blue-400 group-focus-within:text-blue-300 transition-colors" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-3 border border-slate-700 rounded-xl leading-5 bg-slate-800/50 text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all sm:text-sm"
              placeholder="Starting Location..."
              value={start}
              onChange={(e) => setStart(e.target.value)}
            />
          </div>

          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Navigation className="h-5 w-5 text-teal-400 group-focus-within:text-teal-300 transition-colors" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-3 border border-slate-700 rounded-xl leading-5 bg-slate-800/50 text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all sm:text-sm"
              placeholder="Destination..."
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="mt-2 w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-lg text-sm font-bold text-white bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-500 hover:to-teal-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:ring-offset-slate-900 transition-all transform hover:-translate-y-0.5"
          >
            Compute Routes
          </button>
        </form>
      </div>

      {/* Legend */}
      <div className="glass-panel rounded-2xl p-4 flex justify-between text-xs text-slate-300 font-medium shadow-md">
        <div className="flex items-center gap-1"><div className="w-3 h-3 bg-[#10b981] rounded-full"></div> Safest</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 bg-[#f59e0b] rounded-full"></div> Balanced</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 bg-[#ef4444] rounded-full"></div> Shortest</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 bg-blue-500 rounded-full border border-white"></div> Selected</div>
      </div>

      {/* Routes List */}
      {routes.length > 0 && (
        <div className="glass-panel rounded-2xl p-6 flex flex-col gap-4 overflow-y-auto shadow-xl" style={{ maxHeight: '35vh' }}>
          <h3 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            <RouteIcon className="w-5 h-5" />
            Route Options
          </h3>
          
          {routes.map((route, idx) => {
            const isSelected = selectedIndex === idx;
            const distKm = (route.total_distance / 1000).toFixed(2);
            const timeMins = Math.round((route.total_distance / 1000) / 40 * 60); // 40 km/h avg city speed
            
            return (
              <div 
                key={idx}
                onClick={() => onSelectRoute(idx)}
                className={`border rounded-xl p-4 transition-all cursor-pointer relative overflow-hidden group 
                  ${isSelected ? 'bg-slate-700/80 border-blue-500 ring-2 ring-blue-500/50 scale-[1.02]' : 'bg-slate-800/40 border-slate-700 hover:bg-slate-700/60 opacity-70 hover:opacity-100 hover:scale-[1.01]'}`}
              >
                <div className={`absolute top-0 left-0 w-1 h-full`} style={{backgroundColor: route.color}}></div>
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    {idx === 0 ? <ShieldCheck className="w-5 h-5" style={{color: route.color}} /> : <RouteIcon className="w-5 h-5" style={{color: route.color}} />}
                    <span className="font-semibold text-slate-100">{route.type}</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm mt-3">
                  <div className="text-slate-400">Dist: <span className="text-slate-200 font-medium">{distKm} km</span></div>
                  <div className="text-slate-400">Time: <span className="text-slate-200 font-medium">~{timeMins} min</span></div>
                  <div className="col-span-2 text-slate-400 mt-1">Risk Score: <span className="font-bold" style={{color: route.color}}>{Math.round(route.total_risk)}</span></div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Turn by turn */}
      {selectedRoute && turnInstructions.length > 0 && (
        <div className="glass-panel rounded-2xl p-6 flex flex-col gap-3 overflow-y-auto flex-1 shadow-xl">
          <h3 className="text-lg font-semibold text-slate-200 flex items-center gap-2 mb-2">
            <Info className="w-5 h-5" />
            Navigation
          </h3>
          <ul className="text-sm text-slate-300 space-y-3">
            {turnInstructions.map((step, i) => (
              <li key={i} className="flex gap-3 items-start border-b border-slate-700/50 pb-3 last:border-0 last:pb-0">
                <span className="bg-slate-800 border border-slate-600 text-blue-400 w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold shadow-inner">
                  {i+1}
                </span>
                <span className="mt-0.5 leading-relaxed">{step}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
