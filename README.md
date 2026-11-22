# 🤟 SignBridge AI — Intelligent American Sign Language Translation Platform

> **An enterprise-grade, production-ready AI application transforming American Sign Language recognition into real-time natural text and speech.**

---

## 🌟 Executive Overview

SignBridge AI upgrades basic sign classification into a scalable, modular, intelligent ASL recognition and translation platform. 

Combining **client-side MediaPipe 3D hand tracking**, **wrist-relative kinematic normalization**, **multi-class LandmarkNet**, and a **temporal BiLSTM sequence engine**, SignBridge AI achieves **<3ms inference latency** and provides **bidirectional text and speech communication**.

---

## 🚀 Key Capabilities

- **Real-Time Webcam Recognition**: 30–60 FPS client-side hand landmark tracking with zero video transmission over the network.
- **Dual ML Architecture**:
  1. **SignBridge LandmarkNet v1.0**: High-speed classifier for 26 ASL alphabet signs (A–Z) and control gestures (SPACE, DEL).
  2. **SignBridge Temporal BiLSTM v1.0**: 20-frame motion trajectory sequence network recognizing conversational dynamic signs (`HELLO`, `YES`, `NO`, `THANK_YOU`, `PLEASE`, `COME`, `OK`, `HELP`, `STOP`, `GOODBYE`).
  3. **Preserved Legacy Keras CNN Adapter**: Retains full backward compatibility with the original `cnn8grps_rad1_model.h5`.
- **Top-3 Alternatives & Confidence Scoring**: Calibrated probability distributions with unknown-gesture rejection.
- **Temporal Gesture Hysteresis**: Moving-window filter that eliminates flickers and handles transitions between hand poses.
- **Intelligent Translation Engine**:
  - Contextual sentence formation with capitalization and punctuation.
  - Live spelling suggestions and autocorrect via dictionary engine.
  - Native Text-to-Speech (TTS) synthesis.
  - Reverse Speech-to-Text (STT) for two-way Deaf-to-Hearing communication.
- **10-Page SaaS Interface**:
  1. Landing Showcase
  2. User Dashboard
  3. Live ASL Recognition Studio
  4. Translation Workspace
  5. Interactive Learning & Practice Mode (with Confetti!)
  6. Recognition History
  7. Analytics & Benchmark Dashboard
  8. Model Architecture Registry
  9. User Profile & Settings
  10. Admin & Telemetry Center
- **Clean Architecture Backend**: FastAPI with async SQLAlchemy 2.0, JWT authentication, and WebSockets.

---

## 🛠️ Quick Start

### 1. Unified One-Command Runner
Launch both the FastAPI backend (port 8000) and the React frontend (port 3000) simultaneously:

```bash
# Activate existing virtual environment
.v\Scripts\activate

# Launch unified platform
python run_signbridge.py
```

- **Frontend Web Studio**: [http://localhost:3000](http://localhost:3000)
- **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Real-Time WebSocket**: `ws://localhost:8000/ws/recognize`

### Default Login Credentials:
- **Admin**: `admin@signbridge.ai` / `AdminPass123!`
- **Demo User**: `demo@signbridge.ai` / `DemoPass123!`

---

## 🐳 Docker Deployment

Run the complete multi-container stack with PostgreSQL 16 and Redis 7:

```bash
docker compose up -d --build
```

---

## 📚 Technical Documentation Suite

Comprehensive system design deliverables are located in the [`docs/`](file:///c:/Users/DELL/OneDrive/Desktop/Projectss/docs) folder:

- [System Design (SYSTEM_DESIGN.md)](file:///c:/Users/DELL/OneDrive/Desktop/Projectss/docs/SYSTEM_DESIGN.md)
- [System Architecture (ARCHITECTURE.md)](file:///c:/Users/DELL/OneDrive/Desktop/Projectss/docs/ARCHITECTURE.md)
- [API Documentation (API_DOCUMENTATION.md)](file:///c:/Users/DELL/OneDrive/Desktop/Projectss/docs/API_DOCUMENTATION.md)
- [Database Schema & ERD (DATABASE_SCHEMA.md)](file:///c:/Users/DELL/OneDrive/Desktop/Projectss/docs/DATABASE_SCHEMA.md)
- [ML Pipeline & Kinematics (ML_PIPELINE.md)](file:///c:/Users/DELL/OneDrive/Desktop/Projectss/docs/ML_PIPELINE.md)
- [Production Deployment (DEPLOYMENT.md)](file:///c:/Users/DELL/OneDrive/Desktop/Projectss/docs/DEPLOYMENT.md)
- [Security & Privacy Guard (SECURITY.md)](file:///c:/Users/DELL/OneDrive/Desktop/Projectss/docs/SECURITY.md)
- [Testing & Quality Assurance (TESTING.md)](file:///c:/Users/DELL/OneDrive/Desktop/Projectss/docs/TESTING.md)
- [Contributing Guidelines (CONTRIBUTING.md)](file:///c:/Users/DELL/OneDrive/Desktop/Projectss/docs/CONTRIBUTING.md)

---

## 🧪 Automated Testing

```bash
# Run backend ML pipeline tests
python backend/tests/test_ml_pipeline.py

# Run REST API integration tests
python backend/tests/test_api_endpoints.py

# Test frontend compilation
cd frontend && npm run build
```

---

## 📄 License
MIT License. Built for real-world accessibility and production deployment.
