import React, { useState, useEffect, useRef } from 'react';
import { 
  Video, 
  VideoOff, 
  Volume2, 
  RotateCcw, 
  Delete, 
  Copy, 
  Check, 
  Sparkles, 
  Cpu, 
  Sliders, 
  CheckCircle2, 
  AlertTriangle,
  Play,
  Square,
  RefreshCw
} from 'lucide-react';

export default function StudioPage({ selectedModel, setSelectedModel, showToast }) {
  const [isRecognizing, setIsRecognizing] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [currentPrediction, setCurrentPrediction] = useState({
    label: 'NONE',
    confidence: 0.0,
    is_unknown: true,
    top3: [],
    latency_ms: 0.0,
    stabilized_label: 'NONE'
  });
  const [sentence, setSentence] = useState('');
  const [currentWord, setCurrentWord] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [copied, setCopied] = useState(false);
  const [fps, setFps] = useState(0);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const cameraInstanceRef = useRef(null);
  const handsInstanceRef = useRef(null);
  const lastFrameTimeRef = useRef(performance.now());
  const isRecognizingRef = useRef(false);

  useEffect(() => {
    isRecognizingRef.current = isRecognizing;
  }, [isRecognizing]);

  // Connect WebSocket
  useEffect(() => {
    let wsHost = window.location.host;
    if (import.meta.env.VITE_BACKEND_URL) {
      try {
        const parsedUrl = new URL(import.meta.env.VITE_BACKEND_URL);
        wsHost = parsedUrl.host;
      } catch (e) {
        wsHost = import.meta.env.VITE_BACKEND_URL.replace(/^https?:\/\//, '').replace(/\/.*$/, '');
      }
    }
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${wsHost}/ws/recognize`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[Studio] WebSocket connected to SignBridge backend.');
      ws.send(JSON.stringify({ type: 'init' }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'prediction') {
          setCurrentPrediction({
            label: data.label,
            stabilized_label: data.stabilized_label,
            confidence: data.confidence,
            is_unknown: data.is_unknown,
            top3: data.top3 || [],
            latency_ms: data.latency_ms
          });
        } else if (data.type === 'new_token') {
          setSentence(data.sentence || '');
          setCurrentWord(data.current_word || '');
          setSuggestions(data.suggestions || []);
        } else if (data.type === 'dynamic_word') {
          setSentence(data.sentence || '');
          setCurrentWord(data.current_word || '');
          setSuggestions(data.suggestions || []);
          showToast(`Dynamic Sign Recognized: ${data.word}!`, 'success');
          // Speak dynamic word if speech enabled
          speakText(data.word);
        } else if (data.type === 'sentence_update') {
          setSentence(data.sentence || '');
          setCurrentWord(data.current_word || '');
          setSuggestions(data.suggestions || []);
        }
      } catch (err) {
        console.error('WS parse error:', err);
      }
    };

    ws.onerror = (err) => {
      console.warn('WS error (running in fallback REST mode):', err);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  // Initialize MediaPipe Hands
  const initMediaPipe = async () => {
    if (!window.Hands || !window.Camera) {
      console.warn('MediaPipe library loading via CDN...');
      return;
    }

    try {
      const hands = new window.Hands({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
      });

      hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.6,
        minTrackingConfidence: 0.6
      });

      hands.onResults(onHandResults);
      handsInstanceRef.current = hands;

      if (videoRef.current) {
        const camera = new window.Camera(videoRef.current, {
          onFrame: async () => {
            if (isRecognizingRef.current && videoRef.current && handsInstanceRef.current) {
              await handsInstanceRef.current.send({ image: videoRef.current });
            }
          },
          width: 640,
          height: 480
        });
        camera.start();
        cameraInstanceRef.current = camera;
      }
    } catch (err) {
      console.error('Failed to initialize webcam / MediaPipe:', err);
      setCameraError('Camera access required. Please allow webcam permissions in your browser.');
    }
  };

  // Draw hand skeleton & stream landmarks
  const onHandResults = (results) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Calculate FPS
    const now = performance.now();
    const delta = (now - lastFrameTimeRef.current) / 1000.0;
    lastFrameTimeRef.current = now;
    if (delta > 0) {
      setFps(Math.round(1 / delta));
    }

    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      const landmarks = results.multiHandLandmarks[0];
      const handedness = results.multiHandedness && results.multiHandedness[0] 
        ? results.multiHandedness[0].label 
        : 'Right';

      // Draw skeleton lines
      const connections = [
        [0, 1], [1, 2], [2, 3], [3, 4],       // Thumb
        [0, 5], [5, 6], [6, 7], [7, 8],       // Index
        [5, 9], [9, 10], [10, 11], [11, 12],  // Middle
        [9, 13], [13, 14], [14, 15], [15, 16],// Ring
        [13, 17], [17, 18], [18, 19], [19, 20], // Pinky
        [0, 17]
      ];

      ctx.lineWidth = 3;
      ctx.strokeStyle = '#6366f1';
      ctx.shadowColor = '#818cf8';
      ctx.shadowBlur = 8;

      connections.forEach(([i, j]) => {
        const pt1 = landmarks[i];
        const pt2 = landmarks[j];
        ctx.beginPath();
        ctx.moveTo(pt1.x * canvas.width, pt1.y * canvas.height);
        ctx.lineTo(pt2.x * canvas.width, pt2.y * canvas.height);
        ctx.stroke();
      });

      // Draw joints
      landmarks.forEach((pt, idx) => {
        ctx.beginPath();
        ctx.arc(pt.x * canvas.width, pt.y * canvas.height, idx === 4 || idx === 8 || idx === 12 || idx === 16 || idx === 20 ? 5 : 3.5, 0, 2 * Math.PI);
        ctx.fillStyle = idx === 0 ? '#ec4899' : '#10b981';
        ctx.shadowColor = '#34d399';
        ctx.shadowBlur = 6;
        ctx.fill();
      });

      // Send to WebSocket
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && isRecognizingRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'frame',
          landmarks: landmarks.map(lm => ({ x: lm.x, y: lm.y, z: lm.z })),
          handedness: handedness,
          model: selectedModel
        }));
      }
    }
    ctx.restore();
  };

  const handleStartStop = async () => {
    if (!isRecognizing) {
      setCameraError(null);
      if (!cameraInstanceRef.current) {
        await initMediaPipe();
      }
      setIsRecognizing(true);
      showToast('Live Recognition Studio Started', 'success');
    } else {
      setIsRecognizing(false);
      showToast('Recognition Paused', 'info');
    }
  };

  const speakText = (textToSpeak) => {
    const text = textToSpeak || sentence;
    if (!text || text.trim() === '') return;
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    } else {
      showToast('Text-to-speech not supported in this browser.', 'error');
    }
  };

  const handleClear = () => {
    setSentence('');
    setCurrentWord('');
    setSuggestions([]);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'clear' }));
    }
    showToast('Sentence Cleared', 'info');
  };

  const handleUndo = () => {
    if (sentence.length > 0) {
      const words = sentence.trim().split(' ');
      words.pop();
      setSentence(words.join(' '));
    }
  };

  const handleCopy = () => {
    if (!sentence) return;
    navigator.clipboard.writeText(sentence);
    setCopied(true);
    showToast('Copied to clipboard!', 'success');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSelectSuggestion = (word) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'commit_word', word }));
    } else {
      setSentence(prev => prev + ' ' + word);
      setCurrentWord('');
      setSuggestions([]);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Studio Top Control Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-800/80 gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-white tracking-tight">Live ASL Recognition Studio</h1>
            <span className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>{isRecognizing ? 'STREAMING ACTIVE' : 'STANDBY'}</span>
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time hand tracking, kinematic classification, and speech translation pipeline.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleStartStop}
            className={`flex items-center space-x-2 px-5 py-2.5 rounded-xl font-semibold text-xs shadow-lg transition-all ${
              isRecognizing 
                ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/25' 
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/25'
            }`}
          >
            {isRecognizing ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isRecognizing ? 'Stop Stream' : 'Start Recognition'}</span>
          </button>
        </div>
      </div>

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-6">
        
        {/* Left Video Stage (7 cols) */}
        <div className="lg:col-span-7 flex flex-col space-y-4">
          <div className="relative aspect-[4/3] rounded-2xl overflow-hidden bg-slate-900 border border-slate-800/90 shadow-2xl">
            {/* Live Camera Video Feed */}
            <video
              ref={videoRef}
              className="absolute inset-0 w-full h-full object-cover transform -scale-x-100"
              playsInline
              muted
            />

            {/* Skeleton Overlay Canvas */}
            <canvas
              ref={canvasRef}
              width={640}
              height={480}
              className="absolute inset-0 w-full h-full object-cover transform -scale-x-100 pointer-events-none"
            />

            {/* Error or Standby Overlay */}
            {!isRecognizing && (
              <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center text-center p-6">
                <div className="w-16 h-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
                  <Video className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-bold text-white">Camera Standby</h3>
                <p className="text-xs text-slate-400 max-w-sm mt-1 mb-6">
                  Click 'Start Recognition' to initialize the camera feed and begin real-time landmark tracking.
                </p>
                <button
                  onClick={handleStartStop}
                  className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-500/25 transition"
                >
                  Start Camera Feed
                </button>
              </div>
            )}

            {cameraError && (
              <div className="absolute top-4 left-4 right-4 p-3 rounded-xl bg-rose-950/90 border border-rose-500/30 text-rose-200 text-xs flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 flex-shrink-0 text-rose-400" />
                <span>{cameraError}</span>
              </div>
            )}

            {/* Live Stats Pill Overlay */}
            {isRecognizing && (
              <div className="absolute top-4 left-4 flex items-center space-x-2">
                <div className="px-2.5 py-1 rounded-lg bg-black/60 backdrop-blur-md border border-white/10 text-[11px] font-mono text-emerald-400 flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span>{fps} FPS</span>
                </div>
                <div className="px-2.5 py-1 rounded-lg bg-black/60 backdrop-blur-md border border-white/10 text-[11px] font-mono text-indigo-300">
                  {currentPrediction.latency_ms.toFixed(1)} ms
                </div>
              </div>
            )}
          </div>

          {/* Model & Hand Controls */}
          <div className="glass-panel p-4 rounded-xl flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <span className="text-slate-400">Inference Engine:</span>
              <span className="font-semibold text-slate-200">
                {selectedModel === 'landmarknet' && 'LandmarkNet v1 (Normalized 3D)'}
                {selectedModel === 'dynamic' && 'Temporal BiLSTM (20-Frame Sequence)'}
                {selectedModel === 'legacy' && 'Legacy Keras CNN (Preserved H5)'}
              </span>
            </div>
            <div className="text-slate-400 font-mono text-[11px]">
              21 Keypoints Extracted
            </div>
          </div>
        </div>

        {/* Right Telemetry & Sentence Box (5 cols) */}
        <div className="lg:col-span-5 flex flex-col space-y-6">
          
          {/* Active Prediction Hero Card */}
          <div className="glass-panel p-6 rounded-2xl border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Recognized Sign
              </span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-mono font-bold ${
                currentPrediction.confidence >= 0.7 
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              }`}>
                {(currentPrediction.confidence * 100).toFixed(1)}% Confidence
              </span>
            </div>

            <div className="flex items-baseline space-x-4">
              <div className="text-5xl font-black text-white font-mono tracking-wider min-w-[70px]">
                {currentPrediction.stabilized_label !== 'NONE' ? currentPrediction.stabilized_label : '—'}
              </div>
              <div className="text-xs text-slate-400">
                {currentPrediction.is_unknown ? (
                  <span className="text-amber-400">Awaiting stable hand gesture...</span>
                ) : (
                  <span className="text-emerald-400 flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5 inline mr-1" />
                    Gesture Confirmed
                  </span>
                )}
              </div>
            </div>

            {/* Confidence Progress Bar */}
            <div className="w-full bg-slate-800/80 rounded-full h-2 mt-4 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 h-full transition-all duration-300 rounded-full"
                style={{ width: `${Math.min(currentPrediction.confidence * 100, 100)}%` }}
              />
            </div>

            {/* Top-3 Candidate Alternatives */}
            <div className="mt-6 pt-4 border-t border-slate-800/80">
              <span className="text-[11px] font-semibold text-slate-400 block mb-3 uppercase tracking-wider">
                Top-3 Candidate Predictions
              </span>
              <div className="grid grid-cols-3 gap-2">
                {currentPrediction.top3.length > 0 ? (
                  currentPrediction.top3.map((cand, idx) => (
                    <div key={idx} className="bg-slate-900/90 border border-slate-800 rounded-xl p-2.5 text-center">
                      <div className="font-mono font-bold text-sm text-slate-200">
                        {cand.label || cand.word || '—'}
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                        {((cand.confidence || 0) * 100).toFixed(0)}%
                      </div>
                    </div>
                  ))
                ) : (
                  ['—', '—', '—'].map((placeholder, idx) => (
                    <div key={idx} className="bg-slate-900/40 border border-slate-800/60 rounded-xl p-2.5 text-center text-xs text-slate-600">
                      {placeholder}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Translation & Sentence Box */}
          <div className="glass-panel p-6 rounded-2xl border-slate-800 flex-1 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Translated Sentence
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  {sentence.length} chars
                </span>
              </div>

              {/* Editable Sentence Area */}
              <div className="relative">
                <textarea
                  value={sentence}
                  onChange={(e) => setSentence(e.target.value)}
                  placeholder="Recognized words will form a natural translated sentence here..."
                  className="w-full h-28 bg-slate-900/90 border border-slate-800 rounded-xl p-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 resize-none font-sans"
                />
              </div>

              {/* Autocorrect Suggestions Chips */}
              {suggestions.length > 0 && (
                <div className="mt-3">
                  <span className="text-[11px] text-slate-500 block mb-1.5 font-medium">Suggestions:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {suggestions.map((sugg, i) => (
                      <button
                        key={i}
                        onClick={() => handleSelectSuggestion(sugg)}
                        className="px-2.5 py-1 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/20 text-xs font-medium transition"
                      >
                        +{sugg}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Translation Action Toolbar */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-800/80 mt-4 gap-2">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => speakText()}
                  className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition"
                  title="Speak sentence aloud"
                >
                  <Volume2 className="w-4 h-4 text-indigo-400" />
                  <span>Speak</span>
                </button>

                <button
                  onClick={handleCopy}
                  className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
                  title="Copy sentence"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={handleUndo}
                  className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
                  title="Undo last word"
                >
                  <Delete className="w-4 h-4" />
                </button>

                <button
                  onClick={handleClear}
                  className="flex items-center space-x-1 px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-rose-400 text-xs font-medium transition"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Clear</span>
                </button>
              </div>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
}
