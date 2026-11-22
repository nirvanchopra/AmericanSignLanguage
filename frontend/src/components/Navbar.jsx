import React from 'react';
import { 
  Activity, 
  Video, 
  FileText, 
  BarChart2, 
  Cpu, 
  History, 
  Settings, 
  Shield, 
  GraduationCap, 
  Moon, 
  Sun,
  LayoutDashboard,
  Home
} from 'lucide-react';

export default function Navbar({ 
  currentPage, 
  setCurrentPage, 
  darkMode, 
  setDarkMode, 
  selectedModel, 
  setSelectedModel 
}) {
  const navItems = [
    { id: 'landing', label: 'Home', icon: Home },
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'studio', label: 'Studio', icon: Video, badge: 'LIVE' },
    { id: 'workspace', label: 'Workspace', icon: FileText },
    { id: 'learn', label: 'Learn & Practice', icon: GraduationCap },
    { id: 'history', label: 'History', icon: History },
    { id: 'analytics', label: 'Analytics', icon: BarChart2 },
    { id: 'models', label: 'Models', icon: Cpu },
    { id: 'admin', label: 'Admin', icon: Shield },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <div 
            className="flex items-center space-x-3 cursor-pointer"
            onClick={() => setCurrentPage('landing')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-200 bg-clip-text text-transparent">
                  SignBridge
                </span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  AI v1.0
                </span>
              </div>
              <p className="text-[10px] text-slate-400 hidden sm:block tracking-wider uppercase">
                Intelligent ASL Translation Platform
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`relative flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="ml-1 px-1.5 py-0.2 text-[9px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full animate-pulse">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Right Toolbar Controls */}
          <div className="flex items-center space-x-3">
            {/* Active Model Selector */}
            <div className="hidden sm:flex items-center space-x-2 bg-slate-900/90 border border-slate-800 rounded-lg px-2.5 py-1 text-xs">
              <span className="text-slate-500 font-mono text-[11px]">Model:</span>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer text-xs"
              >
                <option value="landmarknet" className="bg-slate-900 text-slate-200">LandmarkNet v1 (Static)</option>
                <option value="dynamic" className="bg-slate-900 text-slate-200">BiLSTM v1 (Dynamic)</option>
                <option value="legacy" className="bg-slate-900 text-slate-200">Legacy Keras CNN (H5)</option>
              </select>
            </div>

            {/* Dark / Light toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              title="Toggle Dark/Light Mode"
            >
              {darkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-400" />}
            </button>

            {/* User Chip */}
            <div 
              onClick={() => setCurrentPage('settings')}
              className="flex items-center space-x-2 p-1.5 rounded-lg bg-slate-900 border border-slate-800 cursor-pointer hover:border-slate-700 transition"
            >
              <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
                S
              </div>
              <span className="text-xs font-medium text-slate-300 hidden md:block">Sarah J.</span>
            </div>
          </div>

        </div>
      </div>

      {/* Mobile nav drawer */}
      <div className="lg:hidden flex overflow-x-auto px-4 py-2 space-x-2 border-t border-slate-800/60 bg-slate-950">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`flex items-center space-x-1.5 px-3 py-1 rounded-md text-xs whitespace-nowrap ${
                isActive ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
}
