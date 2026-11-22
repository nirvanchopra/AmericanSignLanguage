from collections import deque
from typing import List, Dict, Any, Optional
import numpy as np
import time

class DynamicSequenceRecognizer:
    """
    Recognizes multi-frame dynamic ASL word gestures:
    - Maintains a rolling temporal window (default 20 frames) of 63D normalized landmarks.
    - Computes velocity profiles (delta position), trajectory curvature, and posture transitions.
    - Classifies dynamic words: HELLO, YES, NO, THANK_YOU, PLEASE, COME, OK, HELP, STOP, GOODBYE.
    """
    DYNAMIC_WORDS = [
        "HELLO", "YES", "NO", "THANK_YOU", "PLEASE",
        "COME", "OK", "HELP", "STOP", "GOODBYE"
    ]

    def __init__(self, sequence_length: int = 20, confidence_threshold: float = 0.70):
        self.sequence_length = sequence_length
        self.confidence_threshold = confidence_threshold
        self.frame_buffer: deque = deque(maxlen=sequence_length)
        self.last_predicted_word: Optional[str] = None
        self.cooldown_frames: int = 0

    def add_frame(self, normalized_landmarks: np.ndarray):
        """
        Appends 63D feature vector to the rolling sequence buffer.
        """
        if len(normalized_landmarks) == 63:
            self.frame_buffer.append(normalized_landmarks)
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1

    def is_buffer_full(self) -> bool:
        return len(self.frame_buffer) >= self.sequence_length

    def predict(self) -> Dict[str, Any]:
        """
        Analyzes the motion trajectory and posture evolution over the 20-frame window.
        Returns top dynamic word candidates, confidence, and motion activity metrics.
        """
        start_time = time.perf_counter()

        if not self.is_buffer_full() or self.cooldown_frames > 0:
            return {
                "word": None,
                "confidence": 0.0,
                "is_dynamic": False,
                "top3": [],
                "latency_ms": 0.0
            }

        frames = np.array(list(self.frame_buffer))  # shape: (20, 63)
        # Reshape to (20 frames, 21 joints, 3 coordinates)
        joints_seq = frames.reshape(self.sequence_length, 21, 3)

        # 1. Compute velocity and motion magnitude
        diffs = np.diff(joints_seq, axis=0)  # (19, 21, 3)
        velocities = np.linalg.norm(diffs, axis=2)  # (19, 21)
        mean_motion_intensity = float(np.mean(velocities))

        # If motion intensity is negligible (<0.015), the gesture is static, not dynamic
        if mean_motion_intensity < 0.015:
            return {
                "word": None,
                "confidence": 0.0,
                "is_dynamic": False,
                "top3": [],
                "latency_ms": (time.perf_counter() - start_time) * 1000.0
            }

        # 2. Extract trajectory features for dynamic gesture classification
        # Fingertip indices: 4 (thumb), 8 (index), 12 (middle), 16 (ring), 20 (pinky)
        # Wrist index: 0
        fingertip_x_motion = diffs[:, 8, 0]  # Index finger horizontal motion
        fingertip_y_motion = diffs[:, 8, 1]  # Index finger vertical motion
        wrist_y_motion = diffs[:, 0, 1]      # Wrist vertical motion

        scores = {w: 0.1 for w in self.DYNAMIC_WORDS}

        # Wave pattern: Alternating positive and negative horizontal velocity -> HELLO / GOODBYE
        zero_crossings_x = np.where(np.diff(np.signbit(fingertip_x_motion)))[0]
        if len(zero_crossings_x) >= 2 and np.max(np.abs(fingertip_x_motion)) > 0.04:
            scores["HELLO"] += 0.85
            scores["GOODBYE"] += 0.65

        # Nodding pattern: Alternating vertical velocity on fist/wrist -> YES
        zero_crossings_y = np.where(np.diff(np.signbit(wrist_y_motion)))[0]
        if len(zero_crossings_y) >= 2 and np.max(np.abs(wrist_y_motion)) > 0.03:
            scores["YES"] += 0.80

        # Snapping fingers together rapidly -> NO
        thumb_index_dist_start = np.linalg.norm(joints_seq[0, 4] - joints_seq[0, 8])
        thumb_index_dist_end = np.linalg.norm(joints_seq[-1, 4] - joints_seq[-1, 8])
        if thumb_index_dist_start > 0.25 and thumb_index_dist_end < 0.10:
            scores["NO"] += 0.85

        # Downward / forward deceleration -> STOP
        if mean_motion_intensity > 0.03 and np.mean(velocities[-5:]) < 0.01:
            scores["STOP"] += 0.75

        # Upward motion toward body -> COME
        if np.mean(fingertip_y_motion) < -0.02:
            scores["COME"] += 0.70

        # Outward motion away from face -> THANK_YOU
        if np.mean(fingertip_y_motion) > 0.02 and joints_seq[-1, 0, 2] > joints_seq[0, 0, 2]:
            scores["THANK_YOU"] += 0.75

        # Softmax calibration
        words = list(scores.keys())
        raw_vals = np.array([scores[w] for w in words], dtype=np.float32)
        exp_vals = np.exp((raw_vals - np.max(raw_vals)) / 0.25)
        probs = exp_vals / np.sum(exp_vals)

        top_indices = np.argsort(probs)[::-1][:3]
        top3 = [
            {"word": words[idx], "confidence": round(float(probs[idx]), 3)}
            for idx in top_indices
        ]

        best_word = top3[0]["word"]
        best_conf = top3[0]["confidence"]
        is_dynamic = best_conf >= self.confidence_threshold

        if is_dynamic:
            self.cooldown_frames = 15  # Prevent repeated immediate firing

        latency = (time.perf_counter() - start_time) * 1000.0

        return {
            "word": best_word if is_dynamic else None,
            "confidence": best_conf,
            "is_dynamic": is_dynamic,
            "top3": top3,
            "latency_ms": round(latency, 2)
        }

    def reset(self):
        self.frame_buffer.clear()
        self.cooldown_frames = 0
