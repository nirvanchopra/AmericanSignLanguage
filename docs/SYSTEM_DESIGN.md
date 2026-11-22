# SignBridge AI — System Design Document

## 1. Executive Summary

SignBridge AI is an enterprise-grade AI application transforming isolated American Sign Language (ASL) recognition into a unified, continuous translation and accessibility platform. The system bridges the communication gap between Deaf/Hard-of-Hearing individuals and hearing individuals via real-time computer vision, kinematic normalization, sequence modeling, and bi-directional speech-to-text / text-to-speech.

---

## 2. Architectural Boundaries & Principles

1. **Separation of Concerns**:
   - The computer vision feature extraction occurs in the client's browser, preventing heavy video bandwidth transmission over the network and guaranteeing user privacy.
   - The backend handles high-speed matrix inference, temporal stabilization, grammatical structuring, session telemetry, and user management.
2. **Preservation of Legacy Assets**:
   - The original Keras model `cnn8grps_rad1_model.h5` is encapsulated in `LegacyKerasAdapter`, allowing users and researchers to compare legacy CNN heuristics against modern kinematic landmark models side-by-side.
3. **Graceful Degradation**:
   - If WebSockets drop, the client falls back to REST `/api/v1/recognition/recognize`.
   - If PostgreSQL is absent locally, SQLAlchemy automatically defaults to asynchronous SQLite (`signbridge.db`).
   - If pyenchant dictionary libraries are missing on a host, an internal 1000-word high-frequency English dictionary provides continuous autocorrect and suggestions.

---

## 3. Authentication & Authorization Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant App as Web App
    participant Auth as Auth Endpoint (/api/v1/auth/login)
    participant Sec as Security Engine (Bcrypt / JWT)
    participant DB as Database

    User->>App: Enter email & password
    App->>Auth: POST /api/v1/auth/login
    Auth->>DB: Query user by email
    DB-->>Auth: User record & hashed_password
    Auth->>Sec: verify_password(plain, hash)
    Sec-->>Auth: Verified
    Auth->>Sec: create_access_token (24h) + create_refresh_token (7d)
    Sec-->>Auth: JWT Pair
    Auth-->>App: { access_token, refresh_token, user_profile }
    App->>App: Store access_token in memory / secure storage
    App->>Auth: Subsequent requests with Bearer Header
```

---

## 4. Scalability & Deployment Architecture

```mermaid
graph TD
    Client[Browser Clients - WebRTC/WSS]
    LB[Nginx Reverse Proxy / Load Balancer]
    API1[FastAPI Worker 1]
    API2[FastAPI Worker 2]
    RedisNode[(Redis Cache & PubSub)]
    PGNode[(PostgreSQL 16 Primary)]

    Client -->|Port 80/443| LB
    LB -->|WebSocket / HTTP| API1
    LB -->|WebSocket / HTTP| API2
    API1 --> RedisNode
    API2 --> RedisNode
    API1 --> PGNode
    API2 --> PGNode
```
