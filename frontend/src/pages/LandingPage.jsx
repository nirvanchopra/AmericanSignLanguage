import React from 'react';
import { 
  Activity, 
  Video, 
  Zap, 
  ShieldCheck, 
  Cpu, 
  ArrowRight, 
  Sparkles, 
  Volume2, 
  CheckCircle, 
  Layers
} from 'lucide-react';

export default function LandingPage({ setCurrentPage }) {
  return (
    <div className="relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-600/15 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-1/2 right-10 w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-8 animate-fade-in">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Next-Generation Intelligent ASL Translation Platform</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-tight sm:leading-none mb-6">
          Breaking Barriers with <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Real-Time Sign Language AI
          </span>
        </h1>

        <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-400 mb-10 leading-relaxed">
          SignBridge AI converts American Sign Language (ASL) into fluent natural text and speech with 
          sub-3ms latency. Powered by MediaPipe 3D hand landmarks, temporal BiLSTM sequence networks, 
          and context-aware translation.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={() => setCurrentPage('studio')}
            className="w-full sm:w-auto flex items-center justify-center space-x-3 px-8 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-semibold text-sm shadow-xl shadow-indigo-500/25 transition-all transform hover:-translate-y-0.5"
          >
            <Video className="w-4 h-4" />
            <span>Launch Live Studio</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </button>

          <button
            onClick={() => setCurrentPage('learn')}
            className="w-full sm:w-auto flex items-center justify-center space-x-2 px-6 py-3.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white font-medium text-sm transition"
          >
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span>Interactive Learning Mode</span>
          </button>
        </div>

        {/* Live Metrics Ribbon */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
          <div className="glass-panel p-5 rounded-2xl text-left border-slate-800/80">
            <div className="text-2xl font-black text-white font-mono">&lt; 3 ms</div>
            <div className="text-xs text-slate-400 mt-1">Inference Latency</div>
          </div>
          <div className="glass-panel p-5 rounded-2xl text-left border-slate-800/80">
            <div className="text-2xl font-black text-indigo-400 font-mono">98.4%</div>
            <div className="text-xs text-slate-400 mt-1">Landmark Accuracy</div>
          </div>
          <div className="glass-panel p-5 rounded-2xl text-left border-slate-800/80">
            <div className="text-2xl font-black text-purple-400 font-mono">26 + 10</div>
            <div className="text-xs text-slate-400 mt-1">Alphabet & Dynamic Signs</div>
          </div>
          <div className="glass-panel p-5 rounded-2xl text-left border-slate-800/80">
            <div className="text-2xl font-black text-emerald-400 font-mono">Zero-Lag</div>
            <div className="text-xs text-slate-400 mt-1">Bi-directional Speech</div>
          </div>
        </div>
      </section>

      {/* Architecture Highlights Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-800/60">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-white">Engineered for Industry Standards</h2>
          <p className="text-sm text-slate-400 mt-2">Moving beyond basic image classification into production-grade multi-modal AI.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass-panel p-6 rounded-2xl border-slate-800/80">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Direct Landmark Kinematics</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Eliminates brittle pixel heuristics. Uses 21 3D wrist-normalized coordinates that scale invariant to hand size, distance, and orientation.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl border-slate-800/80">
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-4">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Temporal BiLSTM Engine</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Processes 20-frame motion trajectory sequences to recognize continuous dynamic gestures (Hello, Thank You, Yes, No) with velocity profiling.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl border-slate-800/80">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4">
              <Volume2 className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Intelligent Translation & TTS</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Context-aware spelling suggestions, punctuation formatting, and native voice synthesis with reverse speech-to-text dictation.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
