from collections import deque
from typing import List, Dict, Any, Optional
import numpy as np
import time

class DynamicSequenceRecognizer:
    """
    Recognizes multi-frame dynamic ASL word gestures:
    - Maintains a rolling temporal buffer (default 20 frames) of:
      1) 63D normalized posture landmarks (internal finger states).
      2) 3D screen-space palm center & wrist coordinates (global motion trajectory).
    - Computes velocity profiles, direction zero-crossings, trajectory curvatures, and closure speeds.
    - Accurately classifies conversational dynamic words:
      HELLO, HI, YES, NO, THANK_YOU, PLEASE, COME, OK, HELP, STOP, GOODBYE.
    """
    DYNAMIC_WORDS = [
        "HELLO", "HI", "YES", "NO", "THANK_YOU", "PLEASE",
        "COME", "OK", "HELP", "STOP", "GOODBYE"
    ]

    def __init__(self, sequence_length: int = 20, confidence_threshold: float = 0.55):
        self.sequence_length = sequence_length
        self.confidence_threshold = confidence_threshold
        self.norm_buffer: deque = deque(maxlen=sequence_length)
        self.palm_buffer: deque = deque(maxlen=sequence_length)
        self.wrist_buffer: deque = deque(maxlen=sequence_length)
        self.geom_buffer: deque = deque(maxlen=sequence_length)
        self.cooldown_frames: int = 0
        self.last_predicted_word: Optional[str] = None

    def add_frame(
        self,
        normalized_landmarks: np.ndarray,
        raw_landmarks: Optional[List[Dict[str, float]]] = None,
        geometric_features: Optional[Dict[str, Any]] = None
    ):
        """
        Appends normalized landmarks, screen-space palm coordinates, and kinematic features.
        """
        if len(normalized_landmarks) == 63:
            self.norm_buffer.append(normalized_landmarks)

        if raw_landmarks and len(raw_landmarks) == 21:
            # Palm center calculation from Wrist (0), Index MCP (5), Pinky MCP (17)
            cx = float((raw_landmarks[0].get('x', 0) + raw_landmarks[5].get('x', 0) + raw_landmarks[17].get('x', 0)) / 3.0)
            cy = float((raw_landmarks[0].get('y', 0) + raw_landmarks[5].get('y', 0) + raw_landmarks[17].get('y', 0)) / 3.0)
            cz = float((raw_landmarks[0].get('z', 0) + raw_landmarks[5].get('z', 0) + raw_landmarks[17].get('z', 0)) / 3.0)
            self.palm_buffer.append(np.array([cx, cy, cz], dtype=np.float32))

            wx = float(raw_landmarks[0].get('x', 0))
            wy = float(raw_landmarks[0].get('y', 0))
            wz = float(raw_landmarks[0].get('z', 0))
            self.wrist_buffer.append(np.array([wx, wy, wz], dtype=np.float32))
        elif len(normalized_landmarks) == 63:
            # Fallback if raw landmarks not supplied: use index tip and wrist from normalized vector
            self.palm_buffer.append(np.array([normalized_landmarks[24], normalized_landmarks[25], normalized_landmarks[26]], dtype=np.float32))
            self.wrist_buffer.append(np.array([0.0, 0.0, 0.0], dtype=np.float32))

        if geometric_features:
            self.geom_buffer.append(geometric_features)

        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1

    def is_buffer_full(self) -> bool:
        return len(self.norm_buffer) >= min(12, self.sequence_length)

    def predict(self, geometric_features: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyzes motion trajectories and posture transitions over the temporal window.
        Returns recognized dynamic word, confidence, top3, and activity status.
        """
        start_time = time.perf_counter()

        if len(self.norm_buffer) < 12 or self.cooldown_frames > 0:
            return {
                "word": None,
                "confidence": 0.0,
                "is_dynamic": False,
                "top3": [],
                "latency_ms": 0.0
            }

        # Extract sequence matrices
        norm_seq = np.array(list(self.norm_buffer))       # (N, 63)
        palm_seq = np.array(list(self.palm_buffer))       # (N, 3)
        num_frames = len(palm_seq)

        # Palm velocities and motion intensity
        palm_diffs = np.diff(palm_seq, axis=0)            # (N-1, 3)
        palm_velocities = np.linalg.norm(palm_diffs, axis=1)
        mean_motion = float(np.mean(palm_velocities))

        # Check motion threshold: if hand is perfectly static, skip dynamic checks
        if mean_motion < 0.002:
            return {
                "word": None,
                "confidence": 0.0,
                "is_dynamic": False,
                "top3": [],
                "latency_ms": round((time.perf_counter() - start_time) * 1000.0, 2)
            }

        dx = palm_diffs[:, 0]
        dy = palm_diffs[:, 1]
        x_span = float(np.max(palm_seq[:, 0]) - np.min(palm_seq[:, 0]))
        y_span = float(np.max(palm_seq[:, 1]) - np.min(palm_seq[:, 1]))

        # Count zero crossings of velocity (direction changes)
        zx = len(np.where(np.diff(np.signbit(dx)))[0]) if len(dx) > 1 else 0
        zy = len(np.where(np.diff(np.signbit(dy)))[0]) if len(dy) > 1 else 0

        # Current and recent geometric features
        geom = geometric_features or (self.geom_buffer[-1] if self.geom_buffer else {})
        ext_count = geom.get("extended_count", 0)
        tot_ext = geom.get("total_extended", 0)
        is_fist = geom.get("is_fist", False)

        scores = {w: 0.05 for w in self.DYNAMIC_WORDS}

        # 1. Waving gesture -> "HELLO" / "HI"
        # Characterized by horizontal palm oscillation with open/partially open hand
        if zx >= 2 and x_span > 0.035 and ext_count >= 2:
            scores["HELLO"] += 0.95
            scores["HI"] += 0.50
            scores["GOODBYE"] += 0.30
        elif zx >= 1 and 0.020 < x_span <= 0.045 and ext_count >= 2:
            scores["HI"] += 0.95
            scores["HELLO"] += 0.50

        # 2. Nodding fist gesture -> "YES"
        # Characterized by vertical palm oscillation while holding a fist or compact hand
        if zy >= 2 and y_span > 0.025 and (is_fist or ext_count <= 1):
            scores["YES"] += 0.92

        # 3. Finger pinch/snap gesture -> "NO"
        # Index and middle fingers snap down tightly onto thumb tip
        # Look at distance between joint 4 (thumb tip) and joint 8 (index tip) over time
        if len(norm_seq) >= 10:
            thumb_idx_start = np.linalg.norm(norm_seq[:4, 12:15] - norm_seq[:4, 24:27], axis=1).mean()
            thumb_idx_end = np.linalg.norm(norm_seq[-4:, 12:15] - norm_seq[-4:, 24:27], axis=1).mean()
            if thumb_idx_start > 0.16 and thumb_idx_end < 0.09 and (thumb_idx_start - thumb_idx_end > 0.07):
                scores["NO"] += 0.90

        # 4. Outward / downward motion from chest/chin -> "THANK_YOU"
        # Flat hand moving forward and down steadily
        if ext_count >= 3 and y_span > 0.030 and palm_seq[-1, 1] > palm_seq[0, 1] + 0.025:
            scores["THANK_YOU"] += 0.85

        # 5. Circular rubbing trajectory on chest -> "PLEASE"
        # Both x and y oscillate in quadrature with balanced standard deviations
        std_x = float(np.std(palm_seq[:, 0]))
        std_y = float(np.std(palm_seq[:, 1]))
        if ext_count >= 3 and zx >= 1 and zy >= 1 and std_x > 0.012 and std_y > 0.012:
            ratio = std_x / (std_y + 1e-6)
            if 0.4 < ratio < 2.5:
                scores["PLEASE"] += 0.88

        # 6. Thumbs-up moving upward -> "HELP"
        if (is_fist or geom.get("thumb_up_beside_index")) and y_span > 0.030 and palm_seq[-1, 1] < palm_seq[0, 1] - 0.025:
            scores["HELP"] += 0.85

        # 7. Open palm push forward and halt -> "STOP"
        if tot_ext >= 4 and mean_motion > 0.015 and np.mean(palm_velocities[-4:]) < 0.005:
            scores["STOP"] += 0.85

        # 8. Hand moving inward towards body -> "COME"
        if palm_seq[-1, 2] < palm_seq[0, 2] - 0.04 or (ext_count >= 1 and dy.mean() < -0.015):
            scores["COME"] += 0.75

        # 9. Waving away / departure -> "GOODBYE"
        if zx >= 2 and x_span > 0.04 and palm_seq[-1, 0] > palm_seq[0, 0] + 0.03:
            scores["GOODBYE"] += 0.82

        # 10. OK sign confirmation
        if geom.get("is_ok_shape"):
            scores["OK"] += 0.80

        # Softmax normalization
        words = list(scores.keys())
        raw_vals = np.array([scores[w] for w in words], dtype=np.float32)
        temperature = 0.15
        exp_vals = np.exp((raw_vals - np.max(raw_vals)) / temperature)
        probs = exp_vals / np.sum(exp_vals)

        top_indices = np.argsort(probs)[::-1][:3]
        top3 = [
            {"word": words[idx], "confidence": round(float(probs[idx]), 3)}
            for idx in top_indices
        ]

        best_word = top3[0]["word"]
        best_conf = top3[0]["confidence"]
        is_dynamic = bool(best_conf >= self.confidence_threshold and scores[best_word] >= 0.70)

        if is_dynamic:
            self.cooldown_frames = 15  # Cooldown half-second to prevent repeat triggering
            self.last_predicted_word = best_word

        latency = (time.perf_counter() - start_time) * 1000.0

        return {
            "word": best_word if is_dynamic else None,
            "confidence": best_conf,
            "is_dynamic": is_dynamic,
            "top3": top3,
            "latency_ms": round(latency, 2)
        }

    def reset(self):
        self.norm_buffer.clear()
        self.palm_buffer.clear()
        self.wrist_buffer.clear()
        self.geom_buffer.clear()
        self.cooldown_frames = 0
        self.last_predicted_word = None
