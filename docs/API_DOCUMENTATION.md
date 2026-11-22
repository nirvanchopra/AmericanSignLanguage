# SignBridge AI — REST & WebSocket API Documentation

**Interactive OpenAPI Docs**: `http://localhost:8000/docs`  
**Base URL**: `http://localhost:8000/api/v1`  
**WebSocket Stream**: `ws://localhost:8000/ws/recognize`  

---

## 1. Authentication Endpoints

### `POST /api/v1/auth/register`
Creates a new user and profile.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "Alex Mercer"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": { "id": "...", "email": "user@example.com", "role": "user" }
  }
  ```

### `POST /api/v1/auth/login`
Authenticates credentials and returns JWT token pair.

### `GET /api/v1/auth/me`
Retrieves current authenticated user and profile settings.
- **Headers**: `Authorization: Bearer <access_token>`

---

## 2. Recognition Endpoints

### `POST /api/v1/recognition/recognize`
Stateless REST recognition of 21 MediaPipe hand landmarks.
- **Request Body**:
  ```json
  {
    "landmarks": [
      { "x": 0.52, "y": 0.61, "z": -0.02 },
      ... (21 points)
    ],
    "handedness": "Right",
    "model_preference": "landmarknet"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "label": "A",
    "stabilized_label": "A",
    "confidence": 0.942,
    "is_unknown": false,
    "is_new_token": true,
    "dynamic_word": null,
    "top3": [
      { "label": "A", "confidence": 0.942 },
      { "label": "S", "confidence": 0.031 },
      { "label": "E", "confidence": 0.015 }
    ],
    "latency_ms": 1.82,
    "model_used": "landmarknet"
  }
  ```

### `GET /api/v1/recognition/models`
Returns list of registered model versions, accuracy, framework, and latency.

### `POST /api/v1/recognition/feedback`
Submits user corrections for model auditing.

---

## 3. Translation Endpoints

### `POST /api/v1/translation/process`
Converts tokens into readable text with suggestions and punctuation.
- **Request Body**:
  ```json
  {
    "tokens": ["H", "E", "L", "L", "O", "SPACE", "W", "O", "R", "L", "D"]
  }
  ```
- **Response**:
  ```json
  {
    "sentence": "Hello world.",
    "current_word": "WORLD",
    "suggestions": ["WORLD", "WORLDS", "WORLDLY"],
    "is_valid_word": true,
    "tts_text": "Hello world."
  }
  ```

---

## 4. WebSocket Protocol (`/ws/recognize`)

### Client Messages:
1. **Initialize Session**: `{"type": "init", "session_id": "optional-uuid"}`
2. **Stream Frame**: `{"type": "frame", "landmarks": [...21 points...], "handedness": "Right", "model": "landmarknet"}`
3. **Commit Suggestion**: `{"type": "commit_word", "word": "WORLD"}`
4. **Clear**: `{"type": "clear"}`

### Server Messages:
1. **Live Frame Prediction**: `{"type": "prediction", "label": "A", "confidence": 0.94, "top3": [...], "latency_ms": 1.8}`
2. **New Token Confirmed**: `{"type": "new_token", "token": "A", "sentence": "A", "suggestions": [...]}`
3. **Dynamic Word Detected**: `{"type": "dynamic_word", "word": "HELLO", "sentence": "Hello."}`
