import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar.jsx';
import Toast from './components/Toast.jsx';
import LandingPage from './pages/LandingPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import StudioPage from './pages/StudioPage.jsx';
import WorkspacePage from './pages/WorkspacePage.jsx';
import LearnPage from './pages/LearnPage.jsx';
import HistoryPage from './pages/HistoryPage.jsx';
import AnalyticsPage from './pages/AnalyticsPage.jsx';
import ModelsPage from './pages/ModelsPage.jsx';
import SettingsPage from './pages/SettingsPage.jsx';
import AdminPage from './pages/AdminPage.jsx';

export default function App() {
  const [currentPage, setCurrentPage] = useState('studio');
  const [darkMode, setDarkMode] = useState(true);
  const [selectedModel, setSelectedModel] = useState('landmarknet');
  const [toast, setToast] = useState(null);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
  };

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'}`}>
      {/* Top Navbar */}
      <Navbar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
      />

      {/* Main Page Content */}
      <main className="flex-1">
        {currentPage === 'landing' && <LandingPage setCurrentPage={setCurrentPage} />}
        {currentPage === 'dashboard' && <DashboardPage setCurrentPage={setCurrentPage} />}
        {currentPage === 'studio' && (
          <StudioPage
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
            showToast={showToast}
          />
        )}
        {currentPage === 'workspace' && <WorkspacePage showToast={showToast} />}
        {currentPage === 'learn' && <LearnPage showToast={showToast} />}
        {currentPage === 'history' && <HistoryPage showToast={showToast} />}
        {currentPage === 'analytics' && <AnalyticsPage />}
        {currentPage === 'models' && <ModelsPage />}
        {currentPage === 'settings' && (
          <SettingsPage
            darkMode={darkMode}
            setDarkMode={setDarkMode}
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
            showToast={showToast}
          />
        )}
        {currentPage === 'admin' && <AdminPage />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>SignBridge AI Platform — Production Ready</span>
          </div>
          <div>
            &copy; 2026 SignBridge AI. Clean Architecture & Industry-Level ASL Translation.
          </div>
        </div>
      </footer>

      {/* Global Toast */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
