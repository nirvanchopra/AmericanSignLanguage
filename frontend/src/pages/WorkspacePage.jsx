import React, { useState } from 'react';
import { 
  FileText, 
  Mic, 
  MicOff, 
  Volume2, 
  Copy, 
  Download, 
  Trash2, 
  Check, 
  ArrowLeftRight,
  Sparkles
} from 'lucide-react';

export default function WorkspacePage({ showToast }) {
  const [translatedText, setTranslatedText] = useState(
    "Hello! Welcome to SignBridge AI. This intelligent workspace supports two-way accessible communication."
  );
  const [isListeningSTT, setIsListeningSTT] = useState(false);
  const [copied, setCopied] = useState(false);

  // Reverse Speech-to-Text (STT) for Hearing to Deaf conversation
  const toggleSpeechToText = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      showToast('Speech recognition not supported in this browser.', 'error');
      return;
    }

    if (!isListeningSTT) {
      try {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
          setIsListeningSTT(true);
          showToast('Microphone listening... Speak clearly.', 'info');
        };

        recognition.onresult = (event) => {
          let transcript = '';
          for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
          }
          if (transcript) {
            setTranslatedText(prev => prev + ' [Speech: ' + transcript.trim() + ']');
          }
        };

        recognition.onerror = (err) => {
          console.error('STT error:', err);
          setIsListeningSTT(false);
        };

        recognition.onend = () => {
          setIsListeningSTT(false);
        };

        recognition.start();
      } catch (e) {
        console.error(e);
        setIsListeningSTT(false);
      }
    } else {
      setIsListeningSTT(false);
      showToast('Microphone stopped.', 'info');
    }
  };

  const handleSpeak = () => {
    if (!translatedText) return;
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(translatedText);
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(translatedText);
    setCopied(true);
    showToast('Copied to clipboard!', 'success');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([translatedText], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `SignBridge-Translation-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    showToast('Transcript downloaded as text file.', 'success');
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-white tracking-tight">Translation Workspace</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Bidirectional Audio & Text
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Edit translated text, synthesize natural voice, and enable reverse speech-to-text dictation.
          </p>
        </div>

        {/* Toolbar */}
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleSpeechToText}
            className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border transition ${
              isListeningSTT 
                ? 'bg-rose-600 border-rose-500 text-white animate-pulse' 
                : 'bg-slate-900 border-slate-800 text-slate-300 hover:text-white'
            }`}
          >
            {isListeningSTT ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4 text-rose-400" />}
            <span>{isListeningSTT ? 'Listening...' : 'Reverse Dictation (STT)'}</span>
          </button>

          <button
            onClick={handleSpeak}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition"
          >
            <Volume2 className="w-4 h-4" />
            <span>Speak All</span>
          </button>
        </div>
      </div>

      {/* Editor Main Canvas */}
      <div className="glass-panel rounded-2xl border-slate-800 mt-6 p-6 shadow-2xl">
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800 text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-indigo-400" />
            <span>Transcript Document</span>
          </div>
          <div className="flex items-center space-x-4">
            <span>{translatedText.split(/\s+/).filter(Boolean).length} words</span>
            <span>{translatedText.length} characters</span>
          </div>
        </div>

        <textarea
          value={translatedText}
          onChange={(e) => setTranslatedText(e.target.value)}
          placeholder="Compose or paste your ASL translation here..."
          className="w-full h-96 bg-transparent text-slate-100 placeholder-slate-600 focus:outline-none text-base leading-relaxed font-sans resize-none"
        />

        <div className="flex items-center justify-between pt-4 border-t border-slate-800 mt-4 text-xs">
          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopy}
              className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>

            <button
              onClick={handleDownload}
              className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export TXT</span>
            </button>
          </div>

          <button
            onClick={() => setTranslatedText('')}
            className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-rose-400 transition"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear</span>
          </button>
        </div>
      </div>
    </div>
  );
}
