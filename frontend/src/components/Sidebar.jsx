import React, { useState } from 'react';
import { Search, Navigation, ShieldCheck, MapPin, Route as RouteIcon } from 'lucide-react';

const Sidebar = ({ onRouteCompute }) => {
  const [start, setStart] = useState('');
  const [destination, setDestination] = useState('');

  const handleCompute = (e) => {
    e.preventDefault();
    if (onRouteCompute) {
      onRouteCompute(start, destination);
    }
  };

  return (
    <div className="absolute top-4 left-4 z-10 w-96 flex flex-col gap-4 max-h-[95vh]">
      {/* Brand Header */}
      <div className="glass-panel rounded-2xl p-6 flex items-center gap-4">
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
      <div className="glass-panel rounded-2xl p-6 flex flex-col gap-5">
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
            Compute Safest Route
          </button>
        </form>
      </div>

      {/* Mock Route Stats Panel (To be populated later) */}
      <div className="glass-panel rounded-2xl p-6 flex flex-col gap-4 flex-1 overflow-y-auto">
        <h3 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
          <RouteIcon className="w-5 h-5" />
          Route Options
        </h3>
        
        {/* Safest Route Card */}
        <div className="bg-slate-800/60 border border-teal-500/30 rounded-xl p-4 hover:bg-slate-700/60 transition-colors cursor-pointer relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-1 h-full bg-teal-500"></div>
          <div className="flex justify-between items-start mb-2">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-teal-400" />
              <span className="font-semibold text-teal-50">Safest Route</span>
            </div>
            <span className="text-xs font-bold px-2 py-1 bg-teal-500/20 text-teal-300 rounded-full">Recommended</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm mt-3">
            <div className="text-slate-400">Distance: <span className="text-slate-200 font-medium">4.2 km</span></div>
            <div className="text-slate-400">Time: <span className="text-slate-200 font-medium">12 min</span></div>
            <div className="col-span-2 text-slate-400 mt-1">Safety Score: <span className="text-teal-400 font-bold">94/100</span></div>
          </div>
        </div>

        {/* Shortest Route Card */}
        <div className="bg-slate-800/40 border border-slate-700 rounded-xl p-4 hover:bg-slate-700/40 transition-colors cursor-pointer relative overflow-hidden group opacity-70 hover:opacity-100">
          <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
          <div className="flex justify-between items-start mb-2">
            <div className="flex items-center gap-2">
              <RouteIcon className="w-5 h-5 text-red-400" />
              <span className="font-semibold text-red-50">Shortest Route</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm mt-3">
            <div className="text-slate-400">Distance: <span className="text-slate-200 font-medium">3.8 km</span></div>
            <div className="text-slate-400">Time: <span className="text-slate-200 font-medium">10 min</span></div>
            <div className="col-span-2 text-slate-400 mt-1">Safety Score: <span className="text-red-400 font-bold">62/100</span></div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Sidebar;
