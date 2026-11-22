# SignBridge AI — Database Schema Specification

## 1. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    USERS ||--o| USER_PROFILES : has
    USERS ||--o{ RECOGNITION_SESSIONS : conducts
    USERS ||--o{ AUDIT_LOGS : records
    RECOGNITION_SESSIONS ||--o{ RECOGNITION_PREDICTIONS : contains
    RECOGNITION_SESSIONS ||--o{ TRANSLATION_HISTORY : produces
    MODEL_VERSIONS ||--o{ RECOGNITION_PREDICTIONS : evaluates
    RECOGNITION_PREDICTIONS ||--o| USER_FEEDBACK : receives

    USERS {
        string id PK "UUID"
        string email UK "Indexed"
        string hashed_password
        string full_name
        string role "user | admin | researcher"
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    USER_PROFILES {
        string id PK
        string user_id FK "Cascade delete"
        string preferred_language
        boolean enable_tts_auto
        float speech_rate
        string theme_preference
        float confidence_threshold
    }

    RECOGNITION_SESSIONS {
        string id PK
        string user_id FK "Indexed"
        string session_name
        string session_type
        int total_signs_recognized
        float average_confidence
        int duration_seconds
        datetime created_at
        datetime ended_at
    }

    MODEL_VERSIONS {
        string id PK
        string model_name
        string version_tag UK
        string framework
        string model_type
        json classes
        json input_shape
        float test_accuracy
        float latency_ms
        boolean is_active
        boolean is_default
    }

    RECOGNITION_PREDICTIONS {
        string id PK
        string session_id FK
        string model_version_id FK
        string predicted_label "Indexed"
        float confidence
        json top3_alternatives
        float inference_latency_ms
        boolean is_unknown
        datetime timestamp
    }

    TRANSLATION_HISTORY {
        string id PK
        string session_id FK
        text raw_tokens
        text translated_sentence
        boolean was_edited
        text edited_sentence
        string language
        datetime created_at
    }

    USER_FEEDBACK {
        string id PK
        string prediction_id FK UK
        string user_id FK
        string true_label
        boolean is_correct
        string comment
        datetime created_at
    }

    AUDIT_LOGS {
        string id PK
        string user_id FK
        string action "Indexed"
        string ip_address
        json details
        datetime timestamp
    }
```

---

## 2. Table Specifications & Indexes

- **Primary Keys**: UUID strings (`VARCHAR(36)`) for horizontal sharding compatibility.
- **Indexes**:
  - `users(email)`: Unique B-tree index for rapid login queries.
  - `recognition_sessions(user_id, created_at)`: Compound index for paginated dashboard retrieval.
  - `recognition_predictions(session_id, timestamp)`: High-performance time-series index.
  - `audit_logs(action, timestamp)`: Security filtering and compliance auditing.
