import numpy as np
from typing import List, Dict, Any, Tuple, Optional

class LandmarkNormalizer:
    """
    Standardizes 21 3D hand landmarks from MediaPipe:
    1. Wrist origin centering: Shifts wrist (landmark 0) to (0, 0, 0).
    2. Scale normalization: Normalizes by max hand span / palm dimension so distance from camera does not affect features.
    3. Handedness normalization: Mirrors left hand coordinates along X-axis so one model recognizes both hands.
    4. Distance & angular feature augmentation: Computes key inter-joint distances, finger extension flags,
       and kinematic postures (fist family disambiguation, crossing, spread, hooking, circular shapes).
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
        Calculates comprehensive anatomical and kinematic features:
        - Finger extension flags (Thumb, Index, Middle, Ring, Pinky)
        - Finger extension counts
        - Inter-fingertip and knuckle distances
        - Specific ASL postures:
          * Hooked finger (X)
          * Crossed fingers (R)
          * Spread V (V, PEACE) vs closed U (U)
          * Fist family thumb positions (A, S, E, T, M, N)
          * L-shape (L)
          * Y-shape (Y)
          * ILY sign (I LOVE YOU)
          * OK sign (OK)
          * Circular shapes (C, O)
          * Horizontal pointing (G, H)
          * Downward pointing (P, Q)
        """
        if len(landmarks) != 21:
            return {}

        pts = np.array([[lm.get('x', 0.0), lm.get('y', 0.0), lm.get('z', 0.0)] for lm in landmarks], dtype=np.float32)

        # Distance helper
        def dist(i, j):
            return float(np.linalg.norm(pts[i] - pts[j]))

        # Joint reference indices:
        # Wrist: 0
        # Thumb: 1 (CMC), 2 (MCP), 3 (IP), 4 (TIP)
        # Index: 5 (MCP), 6 (PIP), 7 (DIP), 8 (TIP)
        # Middle: 9 (MCP), 10 (PIP), 11 (DIP), 12 (TIP)
        # Ring: 13 (MCP), 14 (PIP), 15 (DIP), 16 (TIP)
        # Pinky: 17 (MCP), 18 (PIP), 19 (DIP), 20 (TIP)

        d8_wrist = dist(8, 0)
        d6_wrist = dist(6, 0)
        d12_wrist = dist(12, 0)
        d10_wrist = dist(10, 0)
        d16_wrist = dist(16, 0)
        d14_wrist = dist(14, 0)
        d20_wrist = dist(20, 0)
        d18_wrist = dist(18, 0)

        # In MediaPipe screen coords, smaller y is higher (towards top of frame).
        # A finger is extended when tip is higher than PIP and tip-to-wrist dist exceeds PIP-to-wrist.
        is_index_extended = bool((pts[8][1] < pts[6][1]) and (d8_wrist > d6_wrist * 1.10))
        is_middle_extended = bool((pts[12][1] < pts[10][1]) and (d12_wrist > d10_wrist * 1.10))
        is_ring_extended = bool((pts[16][1] < pts[14][1]) and (d16_wrist > d14_wrist * 1.10))
        is_pinky_extended = bool((pts[20][1] < pts[18][1]) and (d20_wrist > d18_wrist * 1.10))

        # Thumb extension: tip distance from thumb MCP and pinky base
        d4_17 = dist(4, 17)
        d2_17 = dist(2, 17)
        d4_2 = dist(4, 2)
        is_thumb_extended = bool((d4_17 > d2_17 * 1.15) or (d4_2 > 0.35))

        # Extended finger counts
        extended_fingers = [is_index_extended, is_middle_extended, is_ring_extended, is_pinky_extended]
        extended_count = sum(extended_fingers)
        total_extended = extended_count + (1 if is_thumb_extended else 0)

        # Key distances
        thumb_index_dist = dist(4, 8)
        index_middle_dist = dist(8, 12)
        middle_ring_dist = dist(12, 16)
        ring_pinky_dist = dist(16, 20)
        thumb_pinky_dist = dist(4, 20)
        thumb_middle_dist = dist(4, 12)
        thumb_ring_dist = dist(4, 16)

        # Hooked index finger (X sign: PIP above MCP, but tip bent downward)
        is_index_hooked = bool(
            (pts[6][1] < pts[5][1]) and (pts[8][1] > pts[6][1] + 0.02) and
            not is_middle_extended and not is_ring_extended and not is_pinky_extended
        )

        # Crossed fingers (R sign: index and middle extended and overlapping/crossing)
        is_crossed = bool(
            is_index_extended and is_middle_extended and
            not is_ring_extended and not is_pinky_extended and
            ((pts[8][0] > pts[12][0]) or (index_middle_dist < 0.06 and dist(5, 9) > 0.08))
        )

        # V vs U separation (Index & Middle extended, Ring & Pinky folded)
        is_two_fingers = bool(is_index_extended and is_middle_extended and not is_ring_extended and not is_pinky_extended)
        is_spread_v = bool(is_two_fingers and index_middle_dist > 0.12 and not is_crossed)
        is_closed_u = bool(is_two_fingers and index_middle_dist <= 0.09 and not is_crossed)

        # 3 fingers (W sign)
        is_three_w = bool(is_index_extended and is_middle_extended and is_ring_extended and not is_pinky_extended)

        # L-shape: Index extended, Thumb extended horizontally (large angle / leftward)
        is_l_shape = bool(
            is_index_extended and not is_middle_extended and not is_ring_extended and not is_pinky_extended and
            is_thumb_extended and (thumb_index_dist > 0.38) and (pts[4][0] < pts[2][0] - 0.08)
        )

        # Y-shape ("hang loose" / shaka): Thumb and Pinky extended, middle 3 curled
        is_y_shape = bool(
            is_thumb_extended and is_pinky_extended and
            not is_index_extended and not is_middle_extended and not is_ring_extended and
            (thumb_pinky_dist > 0.50)
        )

        # ILY gesture ("I LOVE YOU"): Thumb, Index, and Pinky extended; Middle and Ring folded
        is_ily_shape = bool(
            is_thumb_extended and is_index_extended and is_pinky_extended and
            not is_middle_extended and not is_ring_extended and
            (thumb_pinky_dist > 0.45)
        )

        # OK sign: Index tip touches thumb tip in circle; Middle, Ring, Pinky extended up
        is_ok_shape = bool(
            (thumb_index_dist < 0.13) and
            is_middle_extended and is_ring_extended and is_pinky_extended
        )

        # O-shape: All 4 fingertips close to thumb tip forming closed loop
        max_tip_to_thumb = max(thumb_index_dist, thumb_middle_dist, thumb_ring_dist, thumb_pinky_dist)
        is_o_shape = bool((max_tip_to_thumb < 0.22) and not is_index_extended and not is_middle_extended)

        # C-shape: Curled arc with open gap between thumb and fingers
        is_c_shape = bool(
            (0.18 < thumb_index_dist < 0.45) and
            not is_index_extended and not is_middle_extended and not is_pinky_extended and
            (pts[8][2] > pts[5][2] + 0.05 or pts[4][2] > pts[2][2] + 0.05 or abs(pts[8][1] - pts[4][1]) > 0.10)
        )

        # Horizontal pointing (G: index horizontal, H: index+middle horizontal)
        is_horizontal_pointing = bool(
            abs(pts[8][0] - pts[5][0]) > abs(pts[8][1] - pts[5][1]) * 0.70 and
            not is_ring_extended and not is_pinky_extended
        )

        # Downward pointing (P, Q)
        is_downward_pointing = bool((pts[8][1] > pts[5][1] + 0.05) and not is_pinky_extended)

        # Fist family (A, S, E, T, M, N): all 4 fingers folded into palm
        is_fist = bool(extended_count == 0)

        # Thumb position relative to knuckles for fist disambiguation
        thumb_up_beside_index = bool(
            is_fist and (pts[4][1] < pts[2][1]) and (pts[4][0] <= pts[5][0] + 0.02)
        )
        thumb_across_front = bool(
            is_fist and (pts[4][0] > pts[5][0]) and (pts[4][1] > pts[5][1] - 0.02)
        )
        thumb_under_fingertips = bool(
            is_fist and (pts[4][1] >= min(pts[8][1], pts[12][1]) - 0.04) and
            (pts[8][1] > pts[6][1])
        )
        thumb_between_index_middle = bool(
            is_fist and (pts[5][0] <= pts[4][0] <= pts[9][0] + 0.04)
        )
        thumb_under_three = bool(
            is_fist and (pts[4][0] > pts[9][0])
        )
        thumb_under_two = bool(
            is_fist and (pts[5][0] <= pts[4][0] <= pts[9][0])
        )

        return {
            "is_index_extended": is_index_extended,
            "is_middle_extended": is_middle_extended,
            "is_ring_extended": is_ring_extended,
            "is_pinky_extended": is_pinky_extended,
            "is_thumb_extended": is_thumb_extended,
            "extended_count": extended_count,
            "total_extended": total_extended,
            "thumb_index_dist": thumb_index_dist,
            "index_middle_dist": index_middle_dist,
            "middle_ring_dist": middle_ring_dist,
            "ring_pinky_dist": ring_pinky_dist,
            "thumb_pinky_dist": thumb_pinky_dist,
            "thumb_middle_dist": thumb_middle_dist,
            "thumb_ring_dist": thumb_ring_dist,
            "is_fist": is_fist,
            "is_index_hooked": is_index_hooked,
            "is_crossed": is_crossed,
            "is_spread_v": is_spread_v,
            "is_closed_u": is_closed_u,
            "is_three_w": is_three_w,
            "is_l_shape": is_l_shape,
            "is_y_shape": is_y_shape,
            "is_ily_shape": is_ily_shape,
            "is_ok_shape": is_ok_shape,
            "is_o_shape": is_o_shape,
            "is_c_shape": is_c_shape,
            "is_horizontal_pointing": is_horizontal_pointing,
            "is_downward_pointing": is_downward_pointing,
            "thumb_up_beside_index": thumb_up_beside_index,
            "thumb_across_front": thumb_across_front,
            "thumb_under_fingertips": thumb_under_fingertips,
            "thumb_between_index_middle": thumb_between_index_middle,
            "thumb_under_three": thumb_under_three,
            "thumb_under_two": thumb_under_two,
        }
