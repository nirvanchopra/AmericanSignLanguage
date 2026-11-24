import numpy as np
import time
from typing import Dict, List, Any, Tuple
from app.ml.normalizer import LandmarkNormalizer

class LandmarkClassifier:
    """
    High-accuracy, ultra-low-latency kinematic classifier for 26 ASL alphabet letters,
    control gestures (SPACE, DEL), and direct word signs (I_LOVE_YOU, OK, PEACE).
    Operates on 63 normalized landmark coordinates (wrist-relative and scale-invariant).
    Integrates comprehensive canonical 3D templates and anatomical kinematic rule boosts.
    """
    CLASSES = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
        'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
        'U', 'V', 'W', 'X', 'Y', 'Z', 'SPACE', 'DEL',
        'I_LOVE_YOU'
    ]

    def __init__(self, confidence_threshold: float = 0.50):
        self.confidence_threshold = confidence_threshold
        self.templates = self._initialize_canonical_templates()

    def _initialize_canonical_templates(self) -> Dict[str, np.ndarray]:
        """
        Builds anatomically accurate 21-joint 3D kinematic templates for all ASL letters and words.
        """
        templates = {}

        def create_template(thumb_coord, idx_pts, mid_pts, rng_pts, pnk_pts, custom_pts=None):
            arr = np.zeros((21, 3), dtype=np.float32)
            # Palm base structure
            arr[0] = [0.0, 0.0, 0.0]        # Wrist
            arr[1] = [-0.15, -0.16, 0.0]    # Thumb CMC
            arr[2] = [-0.26, -0.30, 0.02]   # Thumb MCP
            arr[3] = [-0.34, -0.42, 0.04]   # Thumb IP
            arr[5] = [-0.14, -0.50, 0.0]    # Index MCP
            arr[9] = [0.0, -0.54, 0.0]      # Middle MCP
            arr[13] = [0.12, -0.50, 0.0]    # Ring MCP
            arr[17] = [0.22, -0.44, 0.0]    # Pinky MCP

            # Finger coordinates: PIP, DIP, TIP
            arr[6] = idx_pts[0]; arr[7] = idx_pts[1]; arr[8] = idx_pts[2]
            arr[10] = mid_pts[0]; arr[11] = mid_pts[1]; arr[12] = mid_pts[2]
            arr[14] = rng_pts[0]; arr[15] = rng_pts[1]; arr[16] = rng_pts[2]
            arr[18] = pnk_pts[0]; arr[19] = pnk_pts[1]; arr[20] = pnk_pts[2]
            arr[4] = thumb_coord

            if custom_pts:
                for idx, pt in custom_pts.items():
                    arr[idx] = pt

            norm = np.linalg.norm(arr, axis=1)
            max_d = np.max(norm)
            if max_d > 0:
                arr = arr / max_d
            return arr.flatten()

        # Standard finger poses: [PIP, DIP, TIP]
        EXT_INDEX = [[-0.14, -0.68, 0.0], [-0.14, -0.82, 0.0], [-0.14, -0.96, 0.0]]
        EXT_MIDDLE = [[0.0, -0.72, 0.0], [0.0, -0.86, 0.0], [0.0, -1.0, 0.0]]
        EXT_RING = [[0.12, -0.68, 0.0], [0.12, -0.82, 0.0], [0.12, -0.95, 0.0]]
        EXT_PINKY = [[0.22, -0.60, 0.0], [0.22, -0.72, 0.0], [0.22, -0.85, 0.0]]

        FOLD_INDEX = [[-0.14, -0.55, 0.06], [-0.14, -0.45, 0.12], [-0.14, -0.35, 0.10]]
        FOLD_MIDDLE = [[0.0, -0.58, 0.06], [0.0, -0.48, 0.12], [0.0, -0.38, 0.10]]
        FOLD_RING = [[0.12, -0.55, 0.06], [0.12, -0.45, 0.12], [0.12, -0.35, 0.10]]
        FOLD_PINKY = [[0.22, -0.48, 0.06], [0.22, -0.40, 0.12], [0.22, -0.32, 0.10]]

        CURVE_INDEX = [[-0.14, -0.62, 0.10], [-0.14, -0.60, 0.20], [-0.14, -0.52, 0.22]]
        CURVE_MIDDLE = [[0.0, -0.66, 0.10], [0.0, -0.64, 0.20], [0.0, -0.56, 0.22]]
        CURVE_RING = [[0.12, -0.62, 0.10], [0.12, -0.60, 0.20], [0.12, -0.52, 0.22]]
        CURVE_PINKY = [[0.22, -0.54, 0.10], [0.22, -0.52, 0.20], [0.22, -0.45, 0.22]]

        # A: Fist with thumb straight up along index
        templates['A'] = create_template([-0.25, -0.58, 0.06], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY)

        # B: 4 fingers extended together, thumb across palm
        templates['B'] = create_template([0.0, -0.32, 0.08], EXT_INDEX, EXT_MIDDLE, EXT_RING, EXT_PINKY)

        # C: Curved open C-shape for all fingers and thumb
        templates['C'] = create_template([-0.28, -0.42, 0.18], CURVE_INDEX, CURVE_MIDDLE, CURVE_RING, CURVE_PINKY)

        # D: Index up, middle/ring/pinky touching thumb
        templates['D'] = create_template(
            [-0.06, -0.42, 0.08], EXT_INDEX,
            [[-0.04, -0.54, 0.08], [-0.05, -0.48, 0.10], [-0.06, -0.42, 0.08]],
            FOLD_RING, FOLD_PINKY
        )

        # E: All fingers bent down tight with tips resting on thumb
        templates['E'] = create_template([-0.04, -0.28, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY)

        # F: Index touching thumb, middle/ring/pinky extended up
        templates['F'] = create_template(
            [-0.14, -0.50, 0.10],
            [[-0.14, -0.60, 0.06], [-0.14, -0.55, 0.10], [-0.14, -0.50, 0.10]],
            EXT_MIDDLE, EXT_RING, EXT_PINKY
        )

        # G: Index pointing horizontally, thumb parallel, other 3 folded
        templates['G'] = create_template(
            [-0.35, -0.48, 0.0],
            [[-0.28, -0.50, 0.0], [-0.42, -0.50, 0.0], [-0.56, -0.50, 0.0]],
            FOLD_MIDDLE, FOLD_RING, FOLD_PINKY
        )

        # H: Index and middle extended horizontally together, ring/pinky folded
        templates['H'] = create_template(
            [-0.15, -0.36, 0.05],
            [[-0.28, -0.50, 0.0], [-0.42, -0.50, 0.0], [-0.56, -0.50, 0.0]],
            [[-0.26, -0.54, 0.0], [-0.40, -0.54, 0.0], [-0.54, -0.54, 0.0]],
            FOLD_RING, FOLD_PINKY
        )

        # I: Pinky extended straight up, index/middle/ring folded, thumb over fingers
        templates['I'] = create_template([0.0, -0.38, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, EXT_PINKY)

        # J: Pinky extended with scoop curve
        templates['J'] = create_template([0.0, -0.38, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, EXT_PINKY)

        # K: Index up, middle slightly forward, thumb upright between them
        templates['K'] = create_template(
            [-0.08, -0.52, 0.06], EXT_INDEX,
            [[-0.04, -0.70, 0.08], [-0.04, -0.84, 0.12], [-0.04, -0.96, 0.14]],
            FOLD_RING, FOLD_PINKY
        )

        # L: Index up, thumb extended out 90 degrees horizontally
        templates['L'] = create_template([-0.55, -0.32, 0.0], EXT_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY)

        # M: Fist with thumb tucked under 3 fingers
        templates['M'] = create_template([0.06, -0.34, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY)

        # N: Fist with thumb tucked under 2 fingers
        templates['N'] = create_template([-0.02, -0.34, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY)

        # O: All fingertips touching thumb tip in a circle
        templates['O'] = create_template(
            [-0.08, -0.46, 0.15],
            [[-0.12, -0.58, 0.10], [-0.10, -0.52, 0.14], [-0.08, -0.46, 0.15]],
            [[-0.02, -0.60, 0.10], [-0.04, -0.54, 0.14], [-0.08, -0.46, 0.15]],
            [[0.08, -0.58, 0.10], [0.04, -0.52, 0.14], [-0.06, -0.46, 0.15]],
            [[0.16, -0.52, 0.10], [0.10, -0.48, 0.14], [-0.05, -0.46, 0.15]]
        )

        # P: Inverted K pointing downward
        templates['P'] = create_template(
            [-0.08, -0.38, 0.06],
            [[-0.14, -0.38, 0.0], [-0.14, -0.24, 0.0], [-0.14, -0.10, 0.0]],
            [[0.0, -0.40, 0.06], [0.0, -0.26, 0.08], [0.0, -0.12, 0.10]],
            FOLD_RING, FOLD_PINKY
        )

        # Q: Inverted G pointing downward
        templates['Q'] = create_template(
            [-0.25, -0.20, 0.0],
            [[-0.14, -0.38, 0.0], [-0.14, -0.24, 0.0], [-0.14, -0.10, 0.0]],
            FOLD_MIDDLE, FOLD_RING, FOLD_PINKY
        )

        # R: Index and middle fingers crossed over each other
        templates['R'] = create_template(
            [0.0, -0.38, 0.08],
            [[-0.10, -0.68, 0.0], [-0.06, -0.82, 0.02], [-0.02, -0.96, 0.04]],
            [[-0.06, -0.72, 0.0], [-0.10, -0.86, -0.02], [-0.14, -1.0, -0.04]],
            FOLD_RING, FOLD_PINKY
        )

        # S: Fist with thumb wrapped across front of fingers
        templates['S'] = create_template([0.02, -0.45, 0.12], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY)

        # T: Fist with thumb between index and middle
        templates['T'] = create_template([-0.08, -0.46, 0.08], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY)

        # U: Index and middle extended straight up and pressed tightly together
        templates['U'] = create_template(
            [0.0, -0.38, 0.08],
            [[-0.08, -0.68, 0.0], [-0.06, -0.82, 0.0], [-0.04, -0.96, 0.0]],
            [[0.02, -0.72, 0.0], [0.03, -0.86, 0.0], [0.04, -1.0, 0.0]],
            FOLD_RING, FOLD_PINKY
        )

        # V: Index and middle extended up and spread apart in peace sign
        templates['V'] = create_template(
            [0.0, -0.35, 0.08],
            [[-0.20, -0.68, 0.0], [-0.26, -0.82, 0.0], [-0.32, -0.96, 0.0]],
            [[0.06, -0.72, 0.0], [0.10, -0.86, 0.0], [0.14, -1.0, 0.0]],
            FOLD_RING, FOLD_PINKY
        )

        # W: Index, middle, ring extended spread apart (W shape)
        templates['W'] = create_template(
            [0.10, -0.35, 0.08],
            [[-0.20, -0.68, 0.0], [-0.26, -0.82, 0.0], [-0.32, -0.96, 0.0]],
            EXT_MIDDLE,
            [[0.18, -0.68, 0.0], [0.22, -0.82, 0.0], [0.26, -0.95, 0.0]],
            FOLD_PINKY
        )

        # X: Index crooked/hooked, middle/ring/pinky folded
        templates['X'] = create_template(
            [-0.20, -0.38, 0.08],
            [[-0.14, -0.64, 0.06], [-0.14, -0.56, 0.14], [-0.14, -0.46, 0.10]],
            FOLD_MIDDLE, FOLD_RING, FOLD_PINKY
        )

        # Y: Thumb and pinky extended out wide, middle 3 curled
        templates['Y'] = create_template(
            [-0.55, -0.35, 0.0], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING,
            [[0.30, -0.60, 0.0], [0.42, -0.72, 0.0], [0.54, -0.85, 0.0]]
        )

        # Z: Index finger pointing forward/tracing
        templates['Z'] = create_template(
            [0.0, -0.38, 0.08],
            [[-0.14, -0.68, 0.0], [-0.14, -0.82, 0.0], [-0.14, -0.96, 0.0]],
            FOLD_MIDDLE, FOLD_RING, FOLD_PINKY
        )

        # Controls & Direct Words
        # SPACE: Open flat palm, all fingers spread
        templates['SPACE'] = create_template(
            [-0.42, -0.42, 0.0],
            [[-0.20, -0.68, 0.0], [-0.26, -0.82, 0.0], [-0.30, -0.96, 0.0]],
            EXT_MIDDLE,
            [[0.18, -0.68, 0.0], [0.22, -0.82, 0.0], [0.26, -0.95, 0.0]],
            [[0.30, -0.60, 0.0], [0.38, -0.72, 0.0], [0.45, -0.85, 0.0]]
        )

        # DEL: Backspace gesture (thumb horizontal out with fist)
        templates['DEL'] = create_template([-0.55, -0.20, 0.0], FOLD_INDEX, FOLD_MIDDLE, FOLD_RING, FOLD_PINKY)

        # I_LOVE_YOU: ILY sign (Thumb, Index, Pinky extended; Middle and Ring folded)
        templates['I_LOVE_YOU'] = create_template(
            [-0.55, -0.35, 0.0], EXT_INDEX, FOLD_MIDDLE, FOLD_RING,
            [[0.28, -0.60, 0.0], [0.38, -0.72, 0.0], [0.48, -0.85, 0.0]]
        )

        return templates

    def predict(
        self,
        normalized_landmarks: np.ndarray,
        geometric_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Infers sign from 63D normalized vector combined with geometric heuristics.
        Returns top-3 candidate classes, calibrated confidence, and unknown detection flag.
        """
        start_time = time.perf_counter()

        if len(normalized_landmarks) != 63:
            return {
                "label": "UNKNOWN",
                "confidence": 0.0,
                "top3": [],
                "is_unknown": True,
                "latency_ms": 0.0
            }

        scores = {}
        norm_a = np.linalg.norm(normalized_landmarks)

        for char, tmpl in self.templates.items():
            dot = np.dot(normalized_landmarks, tmpl)
            norm_b = np.linalg.norm(tmpl)
            cos_sim = dot / (norm_a * norm_b + 1e-8)
            euc_dist = np.linalg.norm(normalized_landmarks - tmpl)

            # Affinity score: 60% cosine similarity, 40% distance proximity
            affinity = float(0.60 * cos_sim + 0.40 * (1.0 / (1.0 + euc_dist)))
            scores[char] = affinity

        # Apply Kinematic Boosts and Penalties
        geom = geometric_features or {}
        ext_count = geom.get("extended_count", 0)
        tot_ext = geom.get("total_extended", 0)
        idx_ext = geom.get("is_index_extended", False)
        mid_ext = geom.get("is_middle_extended", False)
        rng_ext = geom.get("is_ring_extended", False)
        pnk_ext = geom.get("is_pinky_extended", False)
        thb_ext = geom.get("is_thumb_extended", False)

        # 1. Direct Word Gesture: I_LOVE_YOU (Thumb, Index, Pinky extended)
        if geom.get("is_ily_shape"):
            scores["I_LOVE_YOU"] = scores.get("I_LOVE_YOU", 0) + 0.70
            scores["Y"] = scores.get("Y", 0) + 0.30

        # 2. OK shape: Index & Thumb touching circle, Middle, Ring, Pinky extended -> letter F
        if geom.get("is_ok_shape"):
            scores["F"] = scores.get("F", 0) + 0.65

        # 3. Peace / V shape: Index & Middle spread apart, Ring & Pinky folded -> letter V
        if geom.get("is_spread_v"):
            scores["V"] = scores.get("V", 0) + 0.65

        # 4. Closed U sign (Index & Middle touching tightly)
        if geom.get("is_closed_u"):
            scores["U"] = scores.get("U", 0) + 0.65

        # 5. Crossed fingers: R sign
        if geom.get("is_crossed"):
            scores["R"] = scores.get("R", 0) + 0.70

        # 6. Hooked finger: X sign
        if geom.get("is_index_hooked"):
            scores["X"] = scores.get("X", 0) + 0.70

        # 7. L-shape sign (Index upright, Thumb horizontal out)
        if geom.get("is_l_shape"):
            scores["L"] = scores.get("L", 0) + 0.75

        # 8. Y-shape sign (Thumb & Pinky wide out)
        if geom.get("is_y_shape") and not idx_ext:
            scores["Y"] = scores.get("Y", 0) + 0.75

        # 9. 3 fingers extended: W sign
        if geom.get("is_three_w"):
            scores["W"] = scores.get("W", 0) + 0.70

        # 10. Fist family disambiguation (A, S, E, T, M, N)
        if geom.get("is_fist"):
            if geom.get("thumb_up_beside_index"):
                scores["A"] = scores.get("A", 0) + 0.60
            elif geom.get("thumb_across_front"):
                scores["S"] = scores.get("S", 0) + 0.60
            elif geom.get("thumb_under_fingertips"):
                scores["E"] = scores.get("E", 0) + 0.55
            elif geom.get("thumb_between_index_middle"):
                scores["T"] = scores.get("T", 0) + 0.55
            elif geom.get("thumb_under_three"):
                scores["M"] = scores.get("M", 0) + 0.50
            elif geom.get("thumb_under_two"):
                scores["N"] = scores.get("N", 0) + 0.50
            else:
                scores["A"] = scores.get("A", 0) + 0.30

        # 11. Single extended finger
        if idx_ext and not mid_ext and not rng_ext and not pnk_ext:
            if not thb_ext or geom.get("thumb_index_dist", 0) < 0.25:
                scores["D"] = scores.get("D", 0) + 0.55
                scores["Z"] = scores.get("Z", 0) + 0.35

        if pnk_ext and not idx_ext and not mid_ext and not rng_ext:
            if not thb_ext:
                scores["I"] = scores.get("I", 0) + 0.65
                scores["J"] = scores.get("J", 0) + 0.40

        # 12. 4 fingers extended together: B sign
        if ext_count == 4 and not thb_ext:
            scores["B"] = scores.get("B", 0) + 0.65

        # 13. All 5 fingers extended spread: SPACE
        if tot_ext == 5 and geom.get("index_middle_dist", 0) > 0.12:
            scores["SPACE"] = scores.get("SPACE", 0) + 0.65

        # 14. Circular profiles: C and O
        if geom.get("is_c_shape"):
            scores["C"] = scores.get("C", 0) + 0.60

        if geom.get("is_o_shape"):
            scores["O"] = scores.get("O", 0) + 0.60

        # 15. Horizontal pointing: G and H
        if geom.get("is_horizontal_pointing"):
            if idx_ext and mid_ext:
                scores["H"] = scores.get("H", 0) + 0.60
            elif idx_ext:
                scores["G"] = scores.get("G", 0) + 0.60

        # 16. Downward pointing: P and Q
        if geom.get("is_downward_pointing"):
            if idx_ext and mid_ext:
                scores["P"] = scores.get("P", 0) + 0.60
            elif idx_ext:
                scores["Q"] = scores.get("Q", 0) + 0.60

        # Calibrate probabilities with softmax temperature
        labels = list(scores.keys())
        raw_vals = np.array([scores[l] for l in labels], dtype=np.float32)
        temperature = 0.040
        exp_vals = np.exp((raw_vals - np.max(raw_vals)) / temperature)
        probs = exp_vals / np.sum(exp_vals)

        # Sort top 3 candidate predictions
        top_indices = np.argsort(probs)[::-1][:3]
        top3 = [
            {"label": labels[idx], "confidence": round(float(probs[idx]), 3)}
            for idx in top_indices
        ]

        best_label = top3[0]["label"]
        best_conf = top3[0]["confidence"]
        is_unknown = best_conf < self.confidence_threshold

        latency = (time.perf_counter() - start_time) * 1000.0

        return {
            "label": "UNKNOWN" if is_unknown else best_label,
            "confidence": best_conf,
            "top3": top3,
            "is_unknown": is_unknown,
            "latency_ms": round(latency, 2)
        }
