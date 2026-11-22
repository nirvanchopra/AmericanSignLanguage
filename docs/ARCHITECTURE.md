# SignBridge AI — System Architecture & Topology

## 1. High-Level Architecture Overview

SignBridge AI is designed using a **Clean Architecture / Modular Monolith** pattern that decouples the presentation layer, real-time gateway, business domain services, machine learning inference engines, and persistent storage.

```mermaid
graph TD
    subgraph ClientLayer["Presentation Layer (Vite / React 18 / Tailwind)"]
        UI_Studio["Live Recognition Studio (WebAssembly MediaPipe)"]
        UI_Trans["Translation Workspace (TTS / STT Reverse Speech)"]
        UI_Learn["ASL Learning & Practice Studio (Confetti & Badges)"]
        UI_Dash["Analytics, History & Model Registry Dashboards"]
    end

    subgraph Gateway["API Gateway & Real-Time Gateway (FastAPI)"]
        WS_Route["/ws/recognize (WebSocket Streaming Gateway)"]
        REST_Route["/api/v1/* (RESTful API Router)"]
        Auth_Guard["JWT & RBAC Middleware"]
        CORS_Guard["CORS & Timing Middleware"]
    end

    subgraph DomainServices["Service Layer (Clean Architecture)"]
        RecogEngine["Unified Recognition Engine"]
        TransService["Translation & Sentence Engine (PyEnchant / Heuristics)"]
        AudioService["Web Speech TTS / STT Service"]
        SessionService["Session & Analytics Service"]
    end

    subgraph MLEngines["Machine Learning Layer"]
        Norm["3D Landmark Normalizer (Wrist-Centric & Scale Invariant)"]
        LMNet["SignBridge LandmarkNet (28-Class Alphabet Classifier)"]
        BiLSTM["SignBridge Temporal BiLSTM (Dynamic Conversational Signs)"]
        LegacyAdapter["Legacy Keras Adapter (Preserved cnn8grps_rad1_model.h5)"]
        Smoother["Temporal Hysteresis & Moving Window Smoother"]
    end

    subgraph DataLayer["Persistence Layer"]
        DB[(PostgreSQL / SQLite via SQLAlchemy 2.0 Async)]
        Cache[(Redis Cache & Session Rate Limiter)]
    end

    ClientLayer -->|JSON Landmarks over WSS| WS_Route
    ClientLayer -->|HTTP REST Requests| REST_Route
    WS_Route --> RecogEngine
    REST_Route --> DomainServices
    RecogEngine --> Norm
    Norm --> LMNet
    Norm --> BiLSTM
    Norm --> LegacyAdapter
    LMNet --> Smoother
    BiLSTM --> Smoother
    LegacyAdapter --> Smoother
    Smoother --> TransService
    DomainServices --> DataLayer
```

---

## 2. Real-Time WebSocket Communication Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User Webcam
    participant Client as Web Browser (React Studio)
    participant MP as MediaPipe WebAssembly
    participant WS as WebSocket Gateway (/ws/recognize)
    participant Engine as Recognition Engine
    participant DB as Async Database

    User->>Client: Live video frames (30-60 FPS)
    Client->>MP: Process frame in browser
    MP-->>Client: 21 Normalized 3D Landmarks
    Note over Client,WS: Lightweight vector (<2 KB JSON vs 150 KB raw image)
    Client->>WS: send({ type: 'frame', landmarks: [...], model: 'landmarknet' })
    WS->>Engine: process_frame(landmarks)
    Engine->>Engine: Wrist centering & scale normalization
    alt Static Alphabet Gesture
        Engine->>Engine: LandmarkNet Softmax Inference (<2 ms)
    else Dynamic Gesture Sequence
        Engine->>Engine: 20-frame trajectory velocity profiling
    end
    Engine->>Engine: Apply hysteresis & temporal moving window
    alt New Stable Gesture Confirmed
        Engine->>DB: Log prediction event & latency
        WS-->>Client: send({ type: 'new_token', token: 'H', sentence: 'Hello.' })
        Client->>Client: Update sentence box & speech audio
    else Transient Frame
        WS-->>Client: send({ type: 'prediction', label: 'H', confidence: 0.94 })
        Client->>Client: Update live candidate badges & confidence bar
    end
```

---

## 3. Technology Stack Breakdown

| Tier | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, TailwindCSS, Vite, Lucide Icons | Responsive SaaS UI with dark/light mode and 10 dedicated routes |
| **Hand Tracking** | MediaPipe Hands WebAssembly | In-browser client-side 3D landmark extraction (preserves user camera privacy) |
| **Backend API** | FastAPI, Uvicorn, Python 3.10 | Async REST endpoints, OpenAPI docs, and real-time WebSockets |
| **Inference Engines** | PyTorch, Keras 2.11, NumPy, Scikit-learn | Multi-model architecture: LandmarkNet, BiLSTM, and Legacy Keras adapter |
| **Database** | PostgreSQL 16 / aiosqlite, SQLAlchemy 2.0 | Async ORM, migration-ready schema with 8 relational tables |
| **Audio & Speech** | Web Speech API & Pyttsx3 | Real-time text-to-speech output and reverse speech-to-text dictation |
| **DevOps** | Docker, Docker Compose, GitHub Actions | Multi-container production deployment and automated CI testing |
