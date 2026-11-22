from typing import Dict, List, Any, Optional
from app.ml.normalizer import LandmarkNormalizer
from app.ml.landmark_classifier import LandmarkClassifier
from app.ml.dynamic_sequence_model import DynamicSequenceRecognizer
from app.ml.legacy_adapter import LegacyKerasAdapter
from app.ml.temporal_smoother import TemporalGestureSmoother
from app.core.config import settings

class RecognitionEngine:
    """
    Unified ML recognition facade providing:
    1. Modern LandmarkNet (Static Alphabet & Hand Gestures)
    2. Dynamic Sequence BiLSTM (Conversational Dynamic Signs)
    3. Legacy Keras CNN Adapter (Backward Compatibility)
    4. Temporal Hysteresis & Prediction Smoothing
    """
    def __init__(self):
        self.normalizer = LandmarkNormalizer()
        self.landmark_classifier = LandmarkClassifier(confidence_threshold=settings.CONFIDENCE_THRESHOLD)
        self.dynamic_recognizer = DynamicSequenceRecognizer(sequence_length=settings.SEQUENCE_BUFFER_LENGTH)
        self.legacy_adapter = LegacyKerasAdapter(model_path=settings.LEGACY_MODEL_PATH)
        self.smoother = TemporalGestureSmoother(
            window_size=settings.SMOOTHING_WINDOW,
            confidence_threshold=settings.CONFIDENCE_THRESHOLD
        )

    def process_frame(
        self,
        landmarks: List[Dict[str, float]],
        handedness: str = "Right",
        model_preference: str = "landmarknet",
        raw_pixel_points: Optional[List[List[int]]] = None,
        bbox: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Coordinates normalization, model inference, and temporal stabilization.
        """
        if not landmarks or len(landmarks) != 21:
            return {
                "label": "NONE",
                "stabilized_label": "NONE",
                "confidence": 0.0,
                "is_unknown": True,
                "is_new_token": False,
                "dynamic_word": None,
                "top3": [],
                "latency_ms": 0.0,
                "model_used": model_preference
            }

        # 1. Normalize landmarks
        norm_vector = self.normalizer.normalize_landmarks(landmarks, handedness=handedness)
        geom_features = self.normalizer.extract_geometric_features(landmarks)

        # 2. Add to dynamic sequence buffer
        self.dynamic_recognizer.add_frame(norm_vector)
        dynamic_result = self.dynamic_recognizer.predict()

        # 3. Model Inference based on preference
        if model_preference == "legacy" and raw_pixel_points and len(raw_pixel_points) == 21:
            w = bbox.get("w", 200) if bbox else 200
            h = bbox.get("h", 200) if bbox else 200
            pred = self.legacy_adapter.predict(raw_pixel_points, w, h)
        else:
            # Modern LandmarkNet
            pred = self.landmark_classifier.predict(norm_vector, geom_features)

        # 4. Temporal Smoothing & Hysteresis
        smoothed = self.smoother.process_frame_prediction(
            predicted_label=pred["label"],
            confidence=pred["confidence"],
            top3=pred["top3"]
        )

        return {
            "label": pred["label"],
            "stabilized_label": smoothed["stabilized_label"],
            "active_stable_label": smoothed["active_stable_label"],
            "confidence": pred["confidence"],
            "is_unknown": smoothed["is_unknown"],
            "is_new_token": smoothed["is_new_stable_token"],
            "dynamic_word": dynamic_result.get("word"),
            "dynamic_confidence": dynamic_result.get("confidence", 0.0),
            "top3": pred["top3"],
            "latency_ms": pred["latency_ms"],
            "stability_ratio": smoothed["stability_ratio"],
            "geometric_features": geom_features,
            "model_used": model_preference
        }

    def reset_state(self):
        self.smoother.reset()
        self.dynamic_recognizer.reset()

# Global engine singleton
recognition_engine = RecognitionEngine()
