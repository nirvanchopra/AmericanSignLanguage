# SignBridge AI — Machine Learning Pipeline & Optimization

## 1. Overview of the AI Pipeline

SignBridge AI upgrades the classic ASL classification pipeline to a multi-modal, dual-model architecture:

```
[Webcam Stream] 
       │
       ▼
[MediaPipe Hands WebAssembly] (21 3D Landmarks)
       │
       ▼
[LandmarkNormalizer]
  ├── 1. Wrist Translation to (0,0,0)
  ├── 2. Scale Invariance (Max Palm Dimension)
  └── 3. Handedness Mirroring (Left/Right Hand Parity)
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
[LandmarkNet v1.0]               [DynamicSequenceRecognizer]
(Alphabet & Static Signs)        (20-Frame Trajectory Buffer)
       │                                 │
       └────────────────┬────────────────┘
                        ▼
       [Temporal Gesture Smoother]
         ├── Hysteresis State Machine
         ├── Exponential Moving Average
         └── Unknown Gesture Rejection
                        ▼
       [Intelligent Translation Engine]
         ├── Token Assembler & Boundary Filter
         ├── Autocorrect & Suggestion Engine
         └── Contextual Punctuation Formatter
```

---

## 2. Normalization Mathematics

Given 21 raw MediaPipe landmark points $P_i = (x_i, y_i, z_i)$ for $i \in \{0, \dots, 20\}$, where $P_0$ represents the wrist:

1. **Wrist Translation**:
   $$\tilde{P}_i = P_i - P_0 \quad \implies \quad \tilde{P}_0 = (0, 0, 0)$$

2. **Scale Invariant Normalization**:
   $$d_{\max} = \max_{i} \|\tilde{P}_i\|_2$$
   $$\hat{P}_i = \frac{\tilde{P}_i}{d_{\max} + \epsilon}$$

3. **Left/Right Mirroring**:
   $$\text{If Handedness} = \text{Left}: \quad \hat{x}_i \leftarrow -\hat{x}_i$$

This ensures that whether a user has small or large hands, is sitting 30 cm or 2 meters from the camera, or is left- or right-handed, the normalized vector $\hat{V} \in \mathbb{R}^{63}$ is mathematically invariant.

---

## 3. Dynamic Sequence Engine (BiLSTM)

Dynamic words (such as `HELLO`, `YES`, `NO`, `THANK_YOU`, `PLEASE`, `COME`, `OK`, `HELP`, `STOP`, `GOODBYE`) involve temporal movement.
- A rolling buffer of $T = 20$ frames is maintained.
- Frame-to-frame velocity vectors $\Delta P_i(t) = P_i(t) - P_i(t-1)$ are evaluated to quantify motion magnitude:
  $$\mu_v = \frac{1}{T-1} \sum_{t=1}^{T-1} \frac{1}{21} \sum_{i=0}^{20} \|\Delta P_i(t)\|_2$$
- If $\mu_v < 0.015$, the hand is determined to be static, suppressing false positive dynamic classifications.
- When $\mu_v \ge 0.015$, sequence trajectory classification executes, identifying cyclic waving (Hello), vertical nodding (Yes), or pinches (No).

---

## 4. Legacy Model Preservation

The existing Keras sequential CNN model (`cnn8grps_rad1_model.h5`, 1.12M params) is preserved via `LegacyKerasAdapter`. It renders the 400x400 white skeleton canvas and applies the legacy 8-group heuristic tree, ensuring full backward compatibility.
