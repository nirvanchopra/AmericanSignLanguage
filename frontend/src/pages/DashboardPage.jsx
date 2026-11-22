import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Video, 
  Clock, 
  Zap, 
  TrendingUp, 
  Calendar, 
  CheckCircle2, 
  ArrowRight,
  ShieldAlert
} from 'lucide-react';

export default function DashboardPage({ setCurrentPage }) {
  const [stats, setStats] = useState({
    total_sessions: 12,
    total_signs_recognized: 486,
    average_confidence: 94.2,
    average_latency_ms: 2.1,
    top_signs: [
      { sign: 'A', count: 82 },
      { sign: 'HELLO', count: 64 },
      { sign: 'L', count: 58 },
      { sign: 'YES', count: 47 },
      { sign: 'THANK_YOU', count: 39 },
    ]
  });

  const recentSessions = [
    { id: 'sess-102', name: 'Alphabet Practice #4', signs: 68, conf: 95.1, date: 'Today, 12:45 PM', duration: '6m 12s' },
    { id: 'sess-101', name: 'Conversational Signs', signs: 124, conf: 93.8, date: 'Yesterday, 4:20 PM', duration: '14m 05s' },
    { id: 'sess-100', name: 'Diagnostic Benchmark', signs: 45, conf: 96.0, date: 'Nov 20, 2026', duration: '4m 30s' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Banner */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border-slate-800 mb-8 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none -z-10" />
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 text-xs font-semibold mb-2">
              <span>SignBridge AI Studio</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Welcome back, Sarah
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-xl">
              Your real-time ASL recognition system is operational. All 3 model engines are online with sub-3ms latency.
            </p>
          </div>

          <button
            onClick={() => setCurrentPage('studio')}
            className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/25 transition"
          >
            <Video className="w-4 h-4" />
            <span>Launch Live Studio</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </button>
        </div>
      </div>

      {/* Primary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="glass-panel p-5 rounded-2xl border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Sessions</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400">
              <Calendar className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-white font-mono">{stats.total_sessions}</div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center space-x-1">
            <TrendingUp className="w-3 h-3" />
            <span>+3 new sessions this week</span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Signs Recognized</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-white font-mono">{stats.total_signs_recognized}</div>
          <div className="text-[11px] text-slate-400 mt-1">Both static & dynamic gestures</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Avg. Confidence</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-emerald-400 font-mono">{stats.average_confidence}%</div>
          <div className="text-[11px] text-slate-400 mt-1">Calibrated softmax probability</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Avg. Latency</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-white font-mono">{stats.average_latency_ms} ms</div>
          <div className="text-[11px] text-emerald-400 mt-1">Ultra-low latency inference</div>
        </div>
      </div>

      {/* Two Column Section: Recent Sessions & Top Signs */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Recent Sessions Table (8 cols) */}
        <div className="lg:col-span-8 glass-panel p-6 rounded-2xl border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Recent Recognition Sessions</h3>
            <button 
              onClick={() => setCurrentPage('history')}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
            >
              View All History &rarr;
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800/80 text-slate-500">
                  <th className="pb-3 font-semibold">Session Name</th>
                  <th className="pb-3 font-semibold">Signs</th>
                  <th className="pb-3 font-semibold">Avg. Accuracy</th>
                  <th className="pb-3 font-semibold">Duration</th>
                  <th className="pb-3 font-semibold">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentSessions.map((sess) => (
                  <tr key={sess.id} className="hover:bg-slate-900/40 transition">
                    <td className="py-3 font-medium text-white flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-indigo-500" />
                      <span>{sess.name}</span>
                    </td>
                    <td className="py-3 font-mono text-slate-300">{sess.signs}</td>
                    <td className="py-3 font-mono text-emerald-400">{sess.conf}%</td>
                    <td className="py-3 text-slate-400 font-mono">{sess.duration}</td>
                    <td className="py-3 text-slate-400">{sess.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Top Signs Distribution (4 cols) */}
        <div className="lg:col-span-4 glass-panel p-6 rounded-2xl border-slate-800">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Most Frequent Signs
          </h3>
          <div className="space-y-3">
            {stats.top_signs.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between bg-slate-900/80 p-3 rounded-xl border border-slate-800/80">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/10 font-mono font-bold text-indigo-400 flex items-center justify-center text-sm">
                    {item.sign}
                  </div>
                  <span className="text-xs font-medium text-slate-200">Sign '{item.sign}'</span>
                </div>
                <div className="text-xs font-mono font-bold text-slate-400">
                  {item.count} times
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
