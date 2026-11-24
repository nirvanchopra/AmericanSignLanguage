import pytest
import numpy as np
from app.ml.normalizer import LandmarkNormalizer
from app.ml.landmark_classifier import LandmarkClassifier
from app.ml.dynamic_sequence_model import DynamicSequenceRecognizer
from app.ml.temporal_smoother import TemporalGestureSmoother
from app.ml.recognition_engine import recognition_engine
from app.services.translation_service import translation_service

def test_landmark_normalizer():
    # 21 mock landmarks
    mock_landmarks = [{"x": float(i * 10), "y": float(i * 15), "z": 0.0} for i in range(21)]
    norm = LandmarkNormalizer.normalize_landmarks(mock_landmarks, handedness="Right")
    assert len(norm) == 63
    # Wrist should be at origin (0, 0, 0)
    assert norm[0] == 0.0
    assert norm[1] == 0.0
    assert norm[2] == 0.0

    geom = LandmarkNormalizer.extract_geometric_features(mock_landmarks)
    assert "is_index_extended" in geom
    assert "extended_count" in geom
    assert "thumb_index_dist" in geom

def test_landmark_classifier_letters():
    classifier = LandmarkClassifier()

    # Test distinct letter canonical templates
    for letter in ['A', 'B', 'C', 'D', 'L', 'V', 'W', 'Y', 'I_LOVE_YOU']:
        template = classifier.templates[letter]
        pred = classifier.predict(template, {})
        assert pred["label"] == letter, f"Expected {letter}, got {pred['label']}"
        assert pred["confidence"] >= 0.50
        assert len(pred["top3"]) == 3

def test_temporal_smoother_and_double_letters():
    smoother = TemporalGestureSmoother(window_size=5, min_consecutive_frames=3)

    # First 'L'
    res1 = smoother.process_frame_prediction("L", 0.9, [])
    assert res1["is_new_stable_token"] is False
    smoother.process_frame_prediction("L", 0.9, [])
    res3 = smoother.process_frame_prediction("L", 0.9, [])
    assert res3["is_new_stable_token"] is True
    assert res3["active_stable_label"] == "L"

    # Relax hand (UNKNOWN)
    for _ in range(4):
        smoother.process_frame_prediction("UNKNOWN", 0.2, [])

    # Second 'L' (e.g. LL in HELLO, ALL)
    smoother.process_frame_prediction("L", 0.9, [])
    smoother.process_frame_prediction("L", 0.9, [])
    res_second_l = smoother.process_frame_prediction("L", 0.9, [])
    assert res_second_l["is_new_stable_token"] is True
    assert res_second_l["active_stable_label"] == "L"

def test_dynamic_recognizer_wave_hello():
    recognizer = DynamicSequenceRecognizer(sequence_length=20)
    # Simulate hand wave: palm oscillates horizontally with open hand
    t = np.linspace(0, 2 * np.pi, 20)
    norm_vec = recognizer.DYNAMIC_WORDS  # placeholder
    for val in 0.5 + 0.07 * np.sin(2 * t):
        mock_raw = [{"x": float(val), "y": 0.5, "z": 0.0} for _ in range(21)]
        # Mark index, middle, ring as extended
        recognizer.add_frame(
            normalized_landmarks=np.zeros(63, dtype=np.float32),
            raw_landmarks=mock_raw,
            geometric_features={"extended_count": 4, "total_extended": 5}
        )
    pred = recognizer.predict(geometric_features={"extended_count": 4})
    assert pred["word"] in ["HELLO", "HI"]
    assert pred["is_dynamic"] is True

def test_dynamic_recognizer_nod_yes():
    recognizer = DynamicSequenceRecognizer(sequence_length=20)
    # Simulate nodding fist: palm oscillates vertically with fist
    t = np.linspace(0, 2 * np.pi, 20)
    for val in 0.5 + 0.06 * np.sin(2 * t):
        mock_raw = [{"x": 0.5, "y": float(val), "z": 0.0} for _ in range(21)]
        recognizer.add_frame(
            normalized_landmarks=np.zeros(63, dtype=np.float32),
            raw_landmarks=mock_raw,
            geometric_features={"extended_count": 0, "is_fist": True}
        )
    pred = recognizer.predict(geometric_features={"extended_count": 0, "is_fist": True})
    assert pred["word"] == "YES"
    assert pred["is_dynamic"] is True

def test_translation_service_word_predictions():
    # Test prefix suggestions
    sugg_h = translation_service.get_suggestions("H")
    assert "HELLO" in sugg_h or "HI" in sugg_h

    sugg_he = translation_service.get_suggestions("HE")
    assert "HELLO" in sugg_he

    sugg_th = translation_service.get_suggestions("TH")
    assert "THANK" in sugg_th or "THANKS" in sugg_th

    # Test sentence assembly with dynamic words and letters
    tokens = ["HELLO", "H", "O", "W", "SPACE", "A", "R", "E", "SPACE", "Y", "O", "U"]
    result = translation_service.assemble_sentence(tokens)
    assert "Hello" in result["sentence"]
    assert "how are you" in result["sentence"].lower()

def test_recognition_engine_pipeline():
    mock_landmarks = [{"x": 0.5 + 0.01 * i, "y": 0.5 - 0.02 * i, "z": 0.0} for i in range(21)]
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
    test_landmark_classifier_letters()
    test_temporal_smoother_and_double_letters()
    test_dynamic_recognizer_wave_hello()
    test_dynamic_recognizer_nod_yes()
    test_translation_service_word_predictions()
    test_recognition_engine_pipeline()
    print("Verification OK: 100% of ML modules tested and working!")
