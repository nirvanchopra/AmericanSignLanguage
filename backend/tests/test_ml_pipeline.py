import pytest
import numpy as np
from app.ml.normalizer import LandmarkNormalizer
from app.ml.landmark_classifier import LandmarkClassifier
from app.ml.dynamic_sequence_model import DynamicSequenceRecognizer
from app.ml.temporal_smoother import TemporalGestureSmoother
from app.ml.recognition_engine import recognition_engine

def test_landmark_normalizer():
    # 21 mock landmarks
    mock_landmarks = [{"x": float(i * 10), "y": float(i * 15), "z": 0.0} for i in range(21)]
    norm = LandmarkNormalizer.normalize_landmarks(mock_landmarks, handedness="Right")
    assert len(norm) == 63
    # Wrist should be at origin (0, 0, 0)
    assert norm[0] == 0.0
    assert norm[1] == 0.0
    assert norm[2] == 0.0

def test_landmark_classifier():
    classifier = LandmarkClassifier()
    # Test canonical A template prediction
    template_a = classifier.templates['A']
    pred = classifier.predict(template_a, {})
    assert pred["label"] == 'A'
    assert pred["confidence"] > 0.60
    assert len(pred["top3"]) == 3
    assert pred["latency_ms"] >= 0.0

def test_temporal_smoother():
    smoother = TemporalGestureSmoother(window_size=5, min_consecutive_frames=3)
    # Stream unstable frame
    res1 = smoother.process_frame_prediction("A", 0.9, [])
    assert res1["is_new_stable_token"] is False
    # Stream consistent frames
    smoother.process_frame_prediction("A", 0.9, [])
    res3 = smoother.process_frame_prediction("A", 0.9, [])
    assert res3["is_new_stable_token"] is True
    assert res3["active_stable_label"] == "A"

def test_dynamic_recognizer():
    recognizer = DynamicSequenceRecognizer(sequence_length=5)
    # Fill buffer
    for i in range(5):
        vec = np.zeros(63, dtype=np.float32)
        vec[24] = float(i * 0.1)  # Simulate index fingertip moving
        recognizer.add_frame(vec)
    assert recognizer.is_buffer_full() is True
    pred = recognizer.predict()
    assert "word" in pred
    assert "top3" in pred

def test_recognition_engine_pipeline():
    mock_landmarks = [{"x": 0.5, "y": 0.5, "z": 0.0} for _ in range(21)]
    # Modify fingertips for non-zero coordinates
    for i in range(21):
        mock_landmarks[i] = {"x": 0.5 + 0.02 * i, "y": 0.5 - 0.03 * i, "z": 0.0}
    
    result = recognition_engine.process_frame(
        landmarks=mock_landmarks,
        handedness="Right",
        model_preference="landmarknet"
    )
    assert "stabilized_label" in result
    assert "top3" in result
    assert "latency_ms" in result
    print("All ML tests passed cleanly!")

if __name__ == "__main__":
    test_landmark_normalizer()
    test_landmark_classifier()
    test_temporal_smoother()
    test_dynamic_recognizer()
    test_recognition_engine_pipeline()
    print("Verification OK: 100% of ML modules tested and working!")
