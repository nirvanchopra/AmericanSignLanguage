import React, { useState } from 'react';
import { 
  GraduationCap, 
  Sparkles, 
  Award, 
  CheckCircle2, 
  Flame, 
  Trophy, 
  ArrowRight,
  BookOpen
} from 'lucide-react';
import confetti from 'canvas-confetti';

export default function LearnPage({ showToast }) {
  const [selectedTargetSign, setSelectedTargetSign] = useState('A');
  const [userScore, setUserScore] = useState(85);
  const [streak, setStreak] = useState(5);

  const alphabet = Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i));

  const badges = [
    { title: "First Sign", desc: "Recognized your first ASL letter", earned: true, icon: "🎉" },
    { title: "Daily Streak", desc: "Practiced 5 days in a row", earned: true, icon: "🔥" },
    { title: "Alphabet Master", desc: "Accurately formed all 26 letters", earned: false, icon: "👑" },
    { title: "Dynamic Guru", desc: "Mastered conversational gestures", earned: false, icon: "⚡" },
  ];

  const handleTestMatch = () => {
    // Trigger confetti celebration
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 }
    });
    showToast(`Great job! Sign '${selectedTargetSign}' matched with 94% accuracy!`, 'success');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-white tracking-tight">ASL Learning & Practice Studio</h1>
            <span className="flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Flame className="w-3.5 h-3.5" />
              <span>{streak} Day Streak!</span>
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Practice your ASL signs with instant AI accuracy feedback, daily challenges, and achievement badges.
          </p>
        </div>

        <button
          onClick={handleTestMatch}
          className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition"
        >
          <Sparkles className="w-4 h-4" />
          <span>Verify Hand Sign Now</span>
        </button>
      </div>

      {/* Grid: Sign of the Day & Live Challenge */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-6">
        
        {/* Left Target Sign Visualizer (5 cols) */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-2xl border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Target Sign Challenge
              </span>
              <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded-md">
                Sign of the Day
              </span>
            </div>

            <div className="flex flex-col items-center justify-center p-8 bg-slate-900/80 rounded-2xl border border-slate-800/80 mb-6 text-center">
              <div className="text-7xl font-black text-white font-mono mb-2">
                {selectedTargetSign}
              </div>
              <div className="text-xs text-slate-400">
                Form the letter <strong className="text-indigo-400 font-mono text-sm">'{selectedTargetSign}'</strong> in front of your camera.
              </div>
            </div>

            {/* Hint & Kinematic Description */}
            <div className="bg-indigo-950/40 border border-indigo-500/20 p-4 rounded-xl text-xs text-indigo-200">
              <div className="font-semibold mb-1 flex items-center space-x-1.5">
                <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                <span>Kinematic Guide for '{selectedTargetSign}':</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                {selectedTargetSign === 'A' && "Make a compact fist with all fingers folded tightly into the palm, and rest your thumb straight up along the side of the index finger."}
                {selectedTargetSign === 'B' && "Hold all 4 fingers straight up touching together, with your thumb folded across the palm."}
                {selectedTargetSign === 'C' && "Curve all 4 fingers and your thumb to form the letter 'C' shape in profile."}
                {selectedTargetSign === 'L' && "Extend your index finger straight up and your thumb outward horizontally to create an exact 90-degree 'L' shape."}
                {selectedTargetSign !== 'A' && selectedTargetSign !== 'B' && selectedTargetSign !== 'C' && selectedTargetSign !== 'L' && "Position your hand firmly in front of the lens. Keep landmarks visible and steady for 1 second."}
              </p>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-xs">
            <span className="text-slate-400">Target Match Accuracy:</span>
            <span className="font-mono font-bold text-emerald-400">94.2%</span>
          </div>
        </div>

        {/* Right Alphabet Selector & Achievements (7 cols) */}
        <div className="lg:col-span-7 flex flex-col space-y-6">
          
          {/* Alphabet Grid */}
          <div className="glass-panel p-6 rounded-2xl border-slate-800">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Select Sign to Practice
            </h3>
            <div className="grid grid-cols-7 sm:grid-cols-9 gap-2">
              {alphabet.map((letter) => (
                <button
                  key={letter}
                  onClick={() => setSelectedTargetSign(letter)}
                  className={`p-2.5 rounded-xl font-mono text-sm font-bold border transition ${
                    selectedTargetSign === letter
                      ? 'bg-indigo-600 border-indigo-500 text-white shadow-md shadow-indigo-600/30'
                      : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
                  }`}
                >
                  {letter}
                </button>
              ))}
            </div>
          </div>

          {/* Gamification & Achievements Badges */}
          <div className="glass-panel p-6 rounded-2xl border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Achievement Badges
              </h3>
              <span className="text-xs text-indigo-400 font-mono">2 / 4 Unlocked</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {badges.map((b, idx) => (
                <div 
                  key={idx}
                  className={`p-3.5 rounded-xl border flex items-center space-x-3 ${
                    b.earned 
                      ? 'bg-slate-900/90 border-indigo-500/30' 
                      : 'bg-slate-950/40 border-slate-800/60 opacity-60'
                  }`}
                >
                  <div className="text-2xl">{b.icon}</div>
                  <div>
                    <div className="text-xs font-bold text-white flex items-center space-x-1.5">
                      <span>{b.title}</span>
                      {b.earned && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">{b.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
