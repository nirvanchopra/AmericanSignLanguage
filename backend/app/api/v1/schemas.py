from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ----------------- AUTH SCHEMAS -----------------
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserProfileOut(BaseModel):
    preferred_language: str
    enable_tts_auto: bool
    speech_rate: float
    theme_preference: str
    confidence_threshold: float
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    profile: Optional[UserProfileOut] = None

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None
    enable_tts_auto: Optional[bool] = None
    speech_rate: Optional[float] = None
    theme_preference: Optional[str] = None
    confidence_threshold: Optional[float] = None

# ----------------- RECOGNITION SCHEMAS -----------------
class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float = 0.0

class RecognitionRequest(BaseModel):
    landmarks: List[LandmarkPoint]
    handedness: str = "Right"
    model_preference: str = "landmarknet"  # landmarknet, legacy, dynamic
    session_id: Optional[str] = None
    raw_pixel_points: Optional[List[List[int]]] = None
    bbox: Optional[Dict[str, int]] = None

class Top3Candidate(BaseModel):
    label: Optional[str] = None
    word: Optional[str] = None
    confidence: float

class RecognitionResponse(BaseModel):
    label: str
    stabilized_label: str
    confidence: float
    is_unknown: bool
    is_new_token: bool
    dynamic_word: Optional[str] = None
    dynamic_confidence: float = 0.0
    top3: List[Dict[str, Any]]
    latency_ms: float
    model_used: str

class FeedbackCreate(BaseModel):
    prediction_id: str
    true_label: str
    is_correct: bool
    comment: Optional[str] = None

# ----------------- SESSION SCHEMAS -----------------
class SessionCreate(BaseModel):
    session_name: Optional[str] = "Live Studio Session"
    session_type: str = "fingerspelling"

class SessionOut(BaseModel):
    id: str
    user_id: str
    session_name: str
    session_type: str
    total_signs_recognized: int
    average_confidence: float
    duration_seconds: int
    created_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ----------------- TRANSLATION SCHEMAS -----------------
class TranslateRequest(BaseModel):
    tokens: List[str]
    session_id: Optional[str] = None
    current_sentence: Optional[str] = ""

class TranslateResponse(BaseModel):
    sentence: str
    current_word: str
    suggestions: List[str]
    is_valid_word: bool
    tts_text: str

# ----------------- ANALYTICS SCHEMAS -----------------
class ModelVersionOut(BaseModel):
    id: str
    model_name: str
    version_tag: str
    framework: str
    model_type: str
    classes: List[str]
    test_accuracy: Optional[float]
    latency_ms: Optional[float]
    description: Optional[str]
    is_active: bool
    is_default: bool

    class Config:
        from_attributes = True
