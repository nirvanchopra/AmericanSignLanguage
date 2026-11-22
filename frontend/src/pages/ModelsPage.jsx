import React from 'react';
import { Cpu, Layers, Zap, CheckCircle2, Shield, AlertTriangle } from 'lucide-react';

export default function ModelsPage() {
  const models = [
    {
      title: "SignBridge LandmarkNet v1.0",
      tag: "landmarknet-v1.0",
      role: "Default Primary Alphabet Classifier",
      framework: "PyTorch / ONNX / WebAssembly",
      input: "21 normalized 3D keypoints (63 float features)",
      output: "28 classes (A-Z, SPACE, DEL)",
      latency: "1.8 ms",
      accuracy: "98.4%",
      desc: "Wrist-relative translation and palm-scale normalization ensure accurate classification regardless of user hand size or distance from the camera. Includes top-3 predictions and unknown gesture rejection.",
      pros: ["Zero reliance on image pixel drawing", "Ultra-low latency (<2ms)", "Invariant to lighting & background noise"]
    },
    {
      title: "SignBridge Temporal BiLSTM v1.0",
      tag: "bilstm-v1.0",
      role: "Dynamic Gesture & Word Sequence Engine",
      framework: "TensorFlow / Keras",
      input: "20 frames × 63 normalized coordinates (20, 63)",
      output: "10 dynamic signs (HELLO, YES, NO, THANK_YOU, PLEASE, COME, OK, HELP, STOP, GOODBYE)",
      latency: "4.5 ms",
      accuracy: "96.2%",
      desc: "Bidirectional Long Short-Term Memory network trained on multi-frame motion trajectories. Differentiates static pauses from active movements through joint velocity profiling.",
      pros: ["Continuous sign recognition", "Velocity and acceleration invariance", "Hysteresis prevents accidental triggers"]
    },
    {
      title: "Legacy 8-Group Keras CNN (Preserved)",
      tag: "cnn8grps-legacy",
      role: "Backward-Compatible Legacy Adapter",
      framework: "Keras 2.11 / H5",
      input: "400 × 400 × 3 synthetic skeleton canvas",
      output: "8 coarse clusters + 450-line geometric heuristic tree",
      latency: "24.5 ms",
      accuracy: "91.5%",
      desc: "Preserved original model 'cnn8grps_rad1_model.h5'. Renders hand skeleton with green lines and red circles onto a white canvas, then executes the original rule tree.",
      pros: ["100% backward compatible", "Preserves original project baseline"],
      cons: ["High latency due to 400x400 image rendering", "Fragile pixel threshold rules"]
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-white tracking-tight">Model Architecture Registry</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              3 Models Deployed
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Technical specifications, input topologies, inference benchmarks, and trade-off analysis.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        {models.map((m, idx) => (
          <div key={idx} className="glass-panel rounded-2xl border-slate-800 p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {m.tag}
                </span>
                <span className="text-xs font-mono font-bold text-emerald-400">
                  {m.accuracy}
                </span>
              </div>

              <h3 className="text-base font-bold text-white mb-1">{m.title}</h3>
              <p className="text-xs font-medium text-slate-400 mb-4">{m.role}</p>

              <p className="text-xs text-slate-300 leading-relaxed mb-6">
                {m.desc}
              </p>

              <div className="space-y-2 border-t border-slate-800/80 pt-4 text-xs font-mono mb-6">
                <div className="flex justify-between">
                  <span className="text-slate-500">Framework:</span>
                  <span className="text-slate-300">{m.framework}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Latency:</span>
                  <span className="text-indigo-400">{m.latency}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Input:</span>
                  <span className="text-slate-300 truncate max-w-[170px]" title={m.input}>{m.input}</span>
                </div>
              </div>
            </div>

            <div className="border-t border-slate-800/80 pt-4">
              <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block mb-2">Key Strengths:</span>
              <ul className="space-y-1">
                {m.pros.map((p, i) => (
                  <li key={i} className="text-xs text-emerald-400 flex items-center space-x-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
                    <span>{p}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
