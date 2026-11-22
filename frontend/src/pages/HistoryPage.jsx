import React, { useState } from 'react';
import { History, Search, Download, Calendar, Clock, CheckCircle2 } from 'lucide-react';

export default function HistoryPage({ showToast }) {
  const [searchTerm, setSearchTerm] = useState('');

  const sessions = [
    { id: 'sess-102', name: 'Alphabet Practice #4', signs: 68, conf: 95.1, date: 'Nov 22, 2026', duration: '6m 12s', transcript: 'HELLO WORLD MY NAME IS SARAH' },
    { id: 'sess-101', name: 'Conversational Signs', signs: 124, conf: 93.8, date: 'Nov 21, 2026', duration: '14m 05s', transcript: 'CAN YOU PLEASE HELP ME WITH DIRECTIONS' },
    { id: 'sess-100', name: 'Diagnostic Benchmark', signs: 45, conf: 96.0, date: 'Nov 20, 2026', duration: '4m 30s', transcript: 'A B C D E F G H I J K L' },
    { id: 'sess-099', name: 'Two-Hand Dynamic Test', signs: 82, conf: 92.5, date: 'Nov 19, 2026', duration: '8m 45s', transcript: 'THANK YOU VERY MUCH SEE YOU TOMORROW' },
    { id: 'sess-098', name: 'Alphabet Drill A-Z', signs: 110, conf: 94.7, date: 'Nov 18, 2026', duration: '11m 20s', transcript: 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG' },
  ];

  const filtered = sessions.filter(s => 
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.transcript.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-white tracking-tight">Recognition History</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              {sessions.length} Saved Sessions
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Complete historical log of all ASL recognition sessions, transcribed sentences, and confidence records.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search transcripts or sessions..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Table */}
      <div className="glass-panel rounded-2xl border-slate-800 mt-6 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/40 text-slate-400 uppercase tracking-wider text-[11px]">
                <th className="p-4 font-semibold">Session Name</th>
                <th className="p-4 font-semibold">Transcript Text</th>
                <th className="p-4 font-semibold">Signs</th>
                <th className="p-4 font-semibold">Confidence</th>
                <th className="p-4 font-semibold">Duration</th>
                <th className="p-4 font-semibold">Date</th>
                <th className="p-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((s) => (
                <tr key={s.id} className="hover:bg-slate-900/50 transition">
                  <td className="p-4 font-semibold text-white whitespace-nowrap">{s.name}</td>
                  <td className="p-4 font-sans text-slate-300 max-w-xs truncate" title={s.transcript}>
                    "{s.transcript}"
                  </td>
                  <td className="p-4 font-mono text-slate-300">{s.signs}</td>
                  <td className="p-4 font-mono text-emerald-400 font-bold">{s.conf}%</td>
                  <td className="p-4 font-mono text-slate-400">{s.duration}</td>
                  <td className="p-4 text-slate-400 whitespace-nowrap">{s.date}</td>
                  <td className="p-4 text-right">
                    <button 
                      onClick={() => showToast(`Transcript for '${s.name}' copied.`, 'success')}
                      className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                    >
                      Copy
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
