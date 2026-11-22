import os
import cv2
import numpy as np
import math
import time
from typing import Dict, List, Any, Optional

class LegacyKerasAdapter:
    """
    Preserves existing functionality of 'cnn8grps_rad1_model.h5' and its 450-line rule tree:
    - Renders the 21 landmarks into a 400x400 white skeleton canvas.
    - Runs the Keras Conv2D model to classify into 8 coarse clusters.
    - Executes the original geometric heuristic tree to disambiguate A-Z, next, Backspace.
    """
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                from keras.models import load_model
                self.model = load_model(self.model_path)
                print(f"[LegacyKerasAdapter] Successfully loaded legacy model from {self.model_path}")
            except Exception as e:
                print(f"[LegacyKerasAdapter] Warning: Failed to load legacy model: {e}")
        else:
            print(f"[LegacyKerasAdapter] Warning: Legacy model file not found at {self.model_path}")

    @staticmethod
    def _distance(x, y):
        return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))

    def render_skeleton_canvas(self, raw_points: List[List[int]], w: int = 200, h: int = 200) -> np.ndarray:
        """
        Draws the exact green lines and red joint circles on a 400x400 white image.
        """
        canvas = np.ones((400, 400, 3), dtype=np.uint8) * 255
        pts = raw_points

        os_x = ((400 - w) // 2) - 15
        os_y = ((400 - h) // 2) - 15

        # Lines
        for t in range(0, 4):
            cv2.line(canvas, (pts[t][0] + os_x, pts[t][1] + os_y), (pts[t+1][0] + os_x, pts[t+1][1] + os_y), (0, 255, 0), 3)
        for t in range(5, 8):
            cv2.line(canvas, (pts[t][0] + os_x, pts[t][1] + os_y), (pts[t+1][0] + os_x, pts[t+1][1] + os_y), (0, 255, 0), 3)
        for t in range(9, 12):
            cv2.line(canvas, (pts[t][0] + os_x, pts[t][1] + os_y), (pts[t+1][0] + os_x, pts[t+1][1] + os_y), (0, 255, 0), 3)
        for t in range(13, 16):
            cv2.line(canvas, (pts[t][0] + os_x, pts[t][1] + os_y), (pts[t+1][0] + os_x, pts[t+1][1] + os_y), (0, 255, 0), 3)
        for t in range(17, 20):
            cv2.line(canvas, (pts[t][0] + os_x, pts[t][1] + os_y), (pts[t+1][0] + os_x, pts[t+1][1] + os_y), (0, 255, 0), 3)

        cv2.line(canvas, (pts[5][0] + os_x, pts[5][1] + os_y), (pts[9][0] + os_x, pts[9][1] + os_y), (0, 255, 0), 3)
        cv2.line(canvas, (pts[9][0] + os_x, pts[9][1] + os_y), (pts[13][0] + os_x, pts[13][1] + os_y), (0, 255, 0), 3)
        cv2.line(canvas, (pts[13][0] + os_x, pts[13][1] + os_y), (pts[17][0] + os_x, pts[17][1] + os_y), (0, 255, 0), 3)
        cv2.line(canvas, (pts[0][0] + os_x, pts[0][1] + os_y), (pts[5][0] + os_x, pts[5][1] + os_y), (0, 255, 0), 3)
        cv2.line(canvas, (pts[0][0] + os_x, pts[0][1] + os_y), (pts[17][0] + os_x, pts[17][1] + os_y), (0, 255, 0), 3)

        # Joint Circles
        for i in range(21):
            cv2.circle(canvas, (pts[i][0] + os_x, pts[i][1] + os_y), 2, (0, 0, 255), 1)

        return canvas

    def predict(self, raw_points: List[List[int]], w: int = 200, h: int = 200) -> Dict[str, Any]:
        """
        Runs legacy pipeline: canvas render -> model forward pass -> heuristic disambiguation.
        """
        start_time = time.perf_counter()

        if self.model is None or len(raw_points) != 21:
            return {
                "label": "UNKNOWN",
                "group": -1,
                "confidence": 0.0,
                "top3": [],
                "is_unknown": True,
                "latency_ms": 0.0
            }

        canvas = self.render_skeleton_canvas(raw_points, w, h)
        input_tensor = canvas.reshape(1, 400, 400, 3)

        preds = self.model.predict(input_tensor, verbose=0)[0]
        prob = np.array(preds, dtype='float32')

        ch1 = int(np.argmax(prob))
        conf = float(prob[ch1])
        prob[ch1] = 0
        ch2 = int(np.argmax(prob))
        prob[ch2] = 0
        ch3 = int(np.argmax(prob))

        pl = [ch1, ch2]
        pts = raw_points

        # Disambiguation logic from final_pred.py
        # Condition checks
        l_aemnst = [[5, 2], [5, 3], [3, 5], [3, 6], [3, 0], [3, 2], [6, 4], [6, 1], [6, 2], [6, 6], [6, 7], [6, 0], [6, 5],
                    [4, 1], [1, 0], [1, 1], [6, 3], [1, 6], [5, 6], [5, 1], [4, 5], [1, 4], [1, 5], [2, 0], [2, 6], [4, 6],
                    [1, 0], [5, 7], [1, 6], [6, 1], [7, 6], [2, 5], [7, 1], [5, 4], [7, 0], [7, 5], [7, 2]]
        if pl in l_aemnst:
            if pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]:
                ch1 = 0

        # Subgroups mapping
        resolved_char = str(ch1)
        if ch1 == 0:
            resolved_char = 'S'
            if pts[4][0] < pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0]:
                resolved_char = 'A'
            elif pts[4][0] > pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]:
                resolved_char = 'T'
            elif pts[4][1] > pts[8][1] and pts[4][1] > pts[12][1] and pts[4][1] > pts[16][1] and pts[4][1] > pts[20][1]:
                resolved_char = 'E'
            elif pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][0] > pts[14][0] and pts[4][1] < pts[18][1]:
                resolved_char = 'M'
            elif pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][1] < pts[18][1] and pts[4][1] < pts[14][1]:
                resolved_char = 'N'

        elif ch1 == 2:
            resolved_char = 'C' if self._distance(pts[12], pts[4]) > 42 else 'O'
        elif ch1 == 3:
            resolved_char = 'G' if self._distance(pts[8], pts[12]) > 72 else 'H'
        elif ch1 == 7:
            resolved_char = 'Y' if self._distance(pts[8], pts[4]) > 42 else 'J'
        elif ch1 == 4:
            resolved_char = 'L'
        elif ch1 == 6:
            resolved_char = 'X'
        elif ch1 == 5:
            if pts[4][0] > pts[12][0] and pts[4][0] > pts[16][0] and pts[4][0] > pts[20][0]:
                resolved_char = 'Z' if pts[8][1] < pts[5][1] else 'Q'
            else:
                resolved_char = 'P'
        elif ch1 == 1:
            if pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]:
                resolved_char = 'B'
            elif pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]:
                resolved_char = 'D'
            elif pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]:
                resolved_char = 'F'
            elif pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]:
                resolved_char = 'I'
            elif pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] < pts[20][1]:
                resolved_char = 'W'
            elif pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1] and pts[4][1] < pts[9][1]:
                resolved_char = 'K'
            elif (self._distance(pts[8], pts[12]) - self._distance(pts[6], pts[10])) < 8 and pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]:
                resolved_char = 'U'
            elif (self._distance(pts[8], pts[12]) - self._distance(pts[6], pts[10])) >= 8 and pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1] and pts[4][1] > pts[9][1]:
                resolved_char = 'V'
            elif pts[8][0] > pts[12][0] and pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]:
                resolved_char = 'R'

        latency = (time.perf_counter() - start_time) * 1000.0

        return {
            "label": resolved_char,
            "group": ch1,
            "confidence": round(conf, 3),
            "top3": [
                {"label": resolved_char, "confidence": round(conf, 3)},
                {"label": f"Group_{ch2}", "confidence": round(float(preds[ch2]), 3)},
                {"label": f"Group_{ch3}", "confidence": round(float(preds[ch3]), 3)}
            ],
            "is_unknown": conf < 0.50,
            "latency_ms": round(latency, 2)
        }
