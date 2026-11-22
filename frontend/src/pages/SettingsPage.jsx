import React, { useState } from 'react';
import { Settings, User, Volume2, Shield, Sliders, Moon, Sun, Save } from 'lucide-react';

export default function SettingsPage({ darkMode, setDarkMode, selectedModel, setSelectedModel, showToast }) {
  const [fullName, setFullName] = useState('Sarah Jenkins');
  const [email, setEmail] = useState('demo@signbridge.ai');
  const [speechRate, setSpeechRate] = useState(1.0);
  const [autoTTS, setAutoTTS] = useState(true);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.65);
  const [allowRecording, setAllowRecording] = useState(false);

  const handleSave = () => {
    showToast('Preferences updated successfully.', 'success');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-800 gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">User Profile & Platform Settings</h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure speech synthesis, recognition thresholds, audio playback, and privacy preferences.
          </p>
        </div>

        <button
          onClick={handleSave}
          className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition"
        >
          <Save className="w-4 h-4" />
          <span>Save Changes</span>
        </button>
      </div>

      <div className="space-y-6">
        
        {/* Profile Card */}
        <div className="glass-panel p-6 rounded-2xl border-slate-800">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-2">
            <User className="w-4 h-4 text-indigo-400" />
            <span>Profile Information</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-400 block mb-1.5 font-medium">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1.5 font-medium">Email Address</label>
              <input
                type="email"
                disabled
                value={email}
                className="w-full bg-slate-900/50 border border-slate-800/60 rounded-xl px-3.5 py-2 text-xs text-slate-400 cursor-not-allowed"
              />
            </div>
          </div>
        </div>

        {/* Speech & Audio Settings */}
        <div className="glass-panel p-6 rounded-2xl border-slate-800">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-2">
            <Volume2 className="w-4 h-4 text-purple-400" />
            <span>Text-to-Speech Engine</span>
          </h3>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-slate-200 block">Automatic Speech Feedback</span>
                <span className="text-[11px] text-slate-400">Speak translated sentences automatically upon pause.</span>
              </div>
              <input
                type="checkbox"
                checked={autoTTS}
                onChange={(e) => setAutoTTS(e.target.checked)}
                className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 bg-slate-900 border-slate-700"
              />
            </div>

            <div className="pt-3 border-t border-slate-800/80">
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-300 font-medium">Speech Rate</span>
                <span className="font-mono text-indigo-400 font-bold">{speechRate}x</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={speechRate}
                onChange={(e) => setSpeechRate(parseFloat(e.target.value))}
                className="w-full accent-indigo-500 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Recognition & Privacy Settings */}
        <div className="glass-panel p-6 rounded-2xl border-slate-800">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            <span>Recognition & Privacy Controls</span>
          </h3>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-300 font-medium">Confidence Rejection Threshold</span>
                <span className="font-mono text-emerald-400 font-bold">{Math.round(confidenceThreshold * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.4"
                max="0.9"
                step="0.05"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                className="w-full accent-emerald-500 cursor-pointer"
              />
              <span className="text-[11px] text-slate-500 block mt-1">
                Gestures below this confidence are filtered out as unknown transit poses.
              </span>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-800/80">
              <div>
                <span className="text-xs font-semibold text-slate-200 block">Camera Privacy (Explicit Consent)</span>
                <span className="text-[11px] text-slate-400">All landmark processing runs in memory. Raw video is never stored on disk.</span>
              </div>
              <span className="text-xs text-emerald-400 font-mono font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                Privacy Guard Active
              </span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
