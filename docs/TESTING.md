# SignBridge AI — Testing & Quality Assurance Suite

## 1. Running the Automated Test Suite

### Backend Unit & Integration Tests:
```bash
# Activate virtual environment
.v\Scripts\activate

# Run Pytest suite
set PYTHONPATH=backend
pytest backend/tests/ -v
```

### Direct Script Verification:
```bash
# 1. Test ML Normalization & Classification Pipeline
python backend/tests/test_ml_pipeline.py

# 2. Test REST Endpoints & Authentication
python backend/tests/test_api_endpoints.py
```

### Frontend Build Verification:
```bash
cd frontend
npm run build
```

---

## 2. Test Coverage Overview

| Module | Test Target | Key Assertions Verified |
| :--- | :--- | :--- |
| `test_ml_pipeline.py` | `LandmarkNormalizer` | Wrist origin translates to (0,0,0); scale invariance |
| `test_ml_pipeline.py` | `LandmarkClassifier` | Top-3 prediction array; latency <2ms; confidence calibrated |
| `test_ml_pipeline.py` | `TemporalSmoother` | Hysteresis state machine rejects transient frame flickers |
| `test_ml_pipeline.py` | `LegacyKerasAdapter` | Loads `cnn8grps_rad1_model.h5` and runs 8-group logic |
| `test_api_endpoints.py`| `/health` | Server uptime and health probe response |
| `test_api_endpoints.py`| `/auth/login` & `/me` | Bcrypt verification and JWT token authorization |
| `test_api_endpoints.py`| `/translation/process`| Token string assembly, word suggestion, and punctuation |
| `test_api_endpoints.py`| `/recognition/recognize`| Real-time REST inference with top-3 predictions |
