import numpy as np
from typing import List, Dict, Any, Tuple, Optional

class LandmarkNormalizer:
    """
    Standardizes 21 3D hand landmarks from MediaPipe:
    1. Wrist origin centering: Shifts wrist (landmark 0) to (0, 0, 0).
    2. Scale normalization: Normalizes by max hand span / palm dimension so distance from camera does not affect features.
    3. Handedness normalization: Mirrors left hand coordinates along X-axis so one model recognizes both hands.
    4. Distance & angular feature augmentation: Computes key inter-joint distances and finger extension flags.
    """

    @staticmethod
    def normalize_landmarks(
        landmarks: List[Dict[str, float]],
        handedness: str = "Right"
    ) -> np.ndarray:
        """
        Input: list of 21 dicts [{'x': ..., 'y': ..., 'z': ...}]
        Output: 63-dimensional normalized numpy array
        """
        if len(landmarks) != 21:
            raise ValueError(f"Expected 21 landmarks, got {len(landmarks)}")

        # Convert to numpy array (21, 3)
        pts = np.array([[lm.get('x', 0.0), lm.get('y', 0.0), lm.get('z', 0.0)] for lm in landmarks], dtype=np.float32)

        # 1. Mirror left hand along x-axis around wrist if left hand
        if handedness.lower() == "left":
            pts[:, 0] = -pts[:, 0]

        # 2. Shift wrist (landmark 0) to origin
        wrist = pts[0].copy()
        pts = pts - wrist

        # 3. Scale normalization: use max distance from wrist to any joint or palm size
        distances = np.linalg.norm(pts, axis=1)
        max_dist = np.max(distances)
        if max_dist > 1e-6:
            pts = pts / max_dist

        return pts.flatten()

    @staticmethod
    def extract_geometric_features(landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Calculates finger state metrics:
        - Finger extension flags (Thumb, Index, Middle, Ring, Pinky)
        - Key fingertip-to-wrist and fingertip-to-thumb distances
        """
        if len(landmarks) != 21:
            return {}

        pts = np.array([[lm['x'], lm['y'], lm['z']] for lm in landmarks], dtype=np.float32)

        # Distance helper
        def dist(i, j):
            return float(np.linalg.norm(pts[i] - pts[j]))

        # Finger tips: 4 (thumb), 8 (index), 12 (middle), 16 (ring), 20 (pinky)
        # Finger PIP joints: 2 (thumb), 6 (index), 10 (middle), 14 (ring), 18 (pinky)
        # Finger MCP joints: 1 (thumb), 5 (index), 9 (middle), 13 (ring), 17 (pinky)
        wrist = 0

        # Vertical extension checks (y decreases upwards in screen coordinates)
        # A finger is extended if tip is higher (smaller y) than PIP joint
        is_index_extended = bool(pts[8][1] < pts[6][1])
        is_middle_extended = bool(pts[12][1] < pts[10][1])
        is_ring_extended = bool(pts[16][1] < pts[14][1])
        is_pinky_extended = bool(pts[20][1] < pts[18][1])
        # Thumb extension (distance from MCP to tip vs wrist)
        is_thumb_extended = bool(dist(4, 17) > dist(2, 17))

        return {
            "is_index_extended": is_index_extended,
            "is_middle_extended": is_middle_extended,
            "is_ring_extended": is_ring_extended,
            "is_pinky_extended": is_pinky_extended,
            "is_thumb_extended": is_thumb_extended,
            "thumb_index_dist": dist(4, 8),
            "index_middle_dist": dist(8, 12),
            "middle_ring_dist": dist(12, 16),
            "ring_pinky_dist": dist(16, 20),
            "thumb_pinky_dist": dist(4, 20)
        }
