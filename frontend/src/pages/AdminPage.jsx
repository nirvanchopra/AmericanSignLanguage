import React from 'react';
import { Shield, Server, Database, Users, Activity, CheckCircle2, AlertTriangle, FileText } from 'lucide-react';

export default function AdminPage() {
  const auditLogs = [
    { id: 'log-1', action: 'MODEL_DEPLOY', user: 'admin@signbridge.ai', details: 'Activated LandmarkNet v1.0', time: '10 mins ago', ip: '127.0.0.1' },
    { id: 'log-2', action: 'USER_REGISTER', user: 'demo@signbridge.ai', details: 'Created account and profile', time: '2 hours ago', ip: '192.168.1.4' },
    { id: 'log-3', action: 'DATABASE_SEED', user: 'system', details: 'Initialized 8 database schemas', time: '3 hours ago', ip: 'internal' },
    { id: 'log-4', action: 'SESSION_COMPLETED', user: 'demo@signbridge.ai', details: 'Session sess-102 transcribed 68 signs', time: '5 hours ago', ip: '192.168.1.4' },
  ];

  const feedbackQueue = [
    { id: 'fb-1', pred: 'S', true_label: 'A', user: 'Sarah J.', comment: 'Thumb was slightly hidden behind index', status: 'Pending Review' },
    { id: 'fb-2', pred: 'V', true_label: 'U', user: 'John D.', comment: 'Fingers were touching, not separated', status: 'Approved for Retrain' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-800 gap-4 mb-8">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-white tracking-tight">Admin & System Control Center</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
              Root Permissions
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Platform telemetry, system health, audit logs, and human-in-the-loop retraining queue.
          </p>
        </div>
      </div>

      {/* System Status Tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="glass-panel p-5 rounded-2xl border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase">API Gateway</span>
            <Server className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl font-bold text-white">FastAPI 0.115</div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Operational (Port 8000)</span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase">Database Engine</span>
            <Database className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-xl font-bold text-white">Async SQLAlchemy</div>
          <div className="text-[11px] text-indigo-400 mt-1">8 Relational Tables</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase">Active Users</span>
            <Users className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-xl font-bold text-white">2 Registered</div>
          <div className="text-[11px] text-slate-400 mt-1">Role-based access enabled</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase">Inference Workers</span>
            <Activity className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-xl font-bold text-white">3 Model Adapters</div>
          <div className="text-[11px] text-emerald-400 mt-1">Real-time WebSocket Ready</div>
        </div>
      </div>

      {/* Two Columns: Audit Logs & Feedback Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Audit Logs (7 cols) */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-2xl border-slate-800">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-2">
            <FileText className="w-4 h-4 text-indigo-400" />
            <span>Platform Security Audit Trail</span>
          </h3>

          <div className="space-y-3">
            {auditLogs.map((log) => (
              <div key={log.id} className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-3 text-xs">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono font-bold text-indigo-400">{log.action}</span>
                  <span className="text-slate-500 font-mono text-[10px]">{log.time}</span>
                </div>
                <div className="text-slate-300 font-medium">{log.details}</div>
                <div className="text-slate-500 text-[10px] mt-1 font-mono">
                  Triggered by: {log.user} ({log.ip})
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Feedback Retraining Queue (5 cols) */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-2xl border-slate-800">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Active Human-in-the-Loop Feedback</span>
          </h3>

          <div className="space-y-3">
            {feedbackQueue.map((item) => (
              <div key={item.id} className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-3.5 text-xs">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-rose-400 line-through">Pred: {item.pred}</span>
                    <span className="font-mono font-bold text-emerald-400">Actual: {item.true_label}</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    {item.status}
                  </span>
                </div>
                <p className="text-slate-400 text-[11px] mb-1 italic">"{item.comment}"</p>
                <div className="text-[10px] text-slate-500">Submitted by {item.user}</div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
