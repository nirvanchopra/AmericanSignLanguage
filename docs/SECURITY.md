# SignBridge AI — Security & Privacy Architecture

## 1. Authentication & Token Strategy
- **Password Storage**: Passwords are mathematically hashed using salted `bcrypt` with automatic truncation to 72 bytes.
- **JWT Lifecycles**:
  - `access_token`: Short-lived (24 hours) for API authorization.
  - `refresh_token`: Rotatable (7 days) stored with strict HTTP-only or secure bearer exchange.
- **Role-Based Access Control (RBAC)**: Route endpoints are strictly partitioned into `user`, `researcher`, and `admin` scopes.

---

## 2. Privacy-Conscious Computer Vision
- **No Remote Video Streaming**: MediaPipe landmark extraction runs natively inside the client's web browser using WebAssembly.
- **Zero Raw Video Stored**: Only lightweight 3D $(x, y, z)$ spatial vectors ($<2\text{ KB/frame}$) are processed. Raw webcam frames never touch server disks or remote cloud storage without explicit user opt-in consent.
- **Biometric Minimization**: Coordinates are normalized relative to wrist origin and scaled to unit length, discarding absolute physical measurements.

---

## 3. Network & Transport Security
- **CORS Protection**: Origin-whitelisting prevents unauthorized third-party domains from querying the API.
- **Rate Limiting**: Throttles brute-force attempts on `/api/v1/auth/login`.
- **SQL Injection Prevention**: Completely mitigated by SQLAlchemy 2.0 parameterized queries and ORM mappings.
