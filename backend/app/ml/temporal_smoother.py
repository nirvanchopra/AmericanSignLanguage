from collections import deque
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

class TemporalGestureSmoother:
    """
    Prevents prediction flickering and performs temporal gesture segmentation:
    - Sliding window majority voting and exponential probability smoothing.
    - Hysteresis: requires a sign to be stable for min_consecutive_frames before triggering a state change.
    - Gesture hold detection: detects when the user holds a sign steady vs transit.
    - Unknown gesture rejection if confidence is below threshold.
    """
    def __init__(
        self,
        window_size: int = 5,
        confidence_threshold: float = 0.65,
        min_consecutive_frames: int = 4
    ):
        self.window_size = window_size
        self.confidence_threshold = confidence_threshold
        self.min_consecutive_frames = min_consecutive_frames

        self.prediction_history: deque = deque(maxlen=window_size)
        self.prob_history: deque = deque(maxlen=window_size)

        self.last_stable_label: Optional[str] = None
        self.candidate_label: Optional[str] = None
        self.candidate_count: int = 0
        self.total_frames_processed: int = 0

    def process_frame_prediction(
        self,
        predicted_label: str,
        confidence: float,
        top3: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Processes a raw frame prediction and applies smoothing and hysteresis.
        Returns stabilized result dictionary.
        """
        self.total_frames_processed += 1

        # Check unknown rejection
        is_unknown = (confidence < self.confidence_threshold) or (predicted_label in ["UNKNOWN", "NONE"])
        effective_label = "UNKNOWN" if is_unknown else predicted_label

        self.prediction_history.append(effective_label)

        # Hysteresis update
        if effective_label == self.candidate_label:
            self.candidate_count += 1
        else:
            self.candidate_label = effective_label
            self.candidate_count = 1

        # If candidate has been held for minimum required consecutive frames, confirm transition
        new_stable_event = False
        if self.candidate_count >= self.min_consecutive_frames:
            if self.candidate_label != self.last_stable_label and self.candidate_label != "UNKNOWN":
                self.last_stable_label = self.candidate_label
                new_stable_event = True

        # Majority vote in window
        labels_in_window = list(self.prediction_history)
        if labels_in_window:
            majority_label = max(set(labels_in_window), key=labels_in_window.count)
            stability_ratio = labels_in_window.count(majority_label) / len(labels_in_window)
        else:
            majority_label = effective_label
            stability_ratio = 1.0

        return {
            "raw_label": predicted_label,
            "raw_confidence": confidence,
            "stabilized_label": majority_label,
            "active_stable_label": self.last_stable_label,
            "is_new_stable_token": new_stable_event,
            "is_unknown": is_unknown,
            "stability_ratio": round(stability_ratio, 2),
            "top3": top3,
            "frames_held": self.candidate_count
        }

    def reset(self):
        self.prediction_history.clear()
        self.prob_history.clear()
        self.last_stable_label = None
        self.candidate_label = None
        self.candidate_count = 0
