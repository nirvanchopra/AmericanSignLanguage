import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class RecognitionSession(Base):
    __tablename__ = "recognition_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_name = Column(String(200), default="Live Studio Session")
    session_type = Column(String(50), default="fingerspelling", nullable=False)  # fingerspelling, dynamic_words, continuous
    total_signs_recognized = Column(Integer, default=0, nullable=False)
    average_confidence = Column(Float, default=0.0, nullable=False)
    duration_seconds = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
    predictions = relationship("RecognitionPrediction", back_populates="session", cascade="all, delete-orphan")
    translations = relationship("TranslationHistory", back_populates="session", cascade="all, delete-orphan")

class RecognitionPrediction(Base):
    __tablename__ = "recognition_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    session_id = Column(String(36), ForeignKey("recognition_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    model_version_id = Column(String(36), ForeignKey("model_versions.id"), nullable=True)
    predicted_label = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    top3_alternatives = Column(JSON, nullable=True)  # [{"label": "A", "confidence": 0.88}, ...]
    inference_latency_ms = Column(Float, nullable=True)
    is_unknown = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    session = relationship("RecognitionSession", back_populates="predictions")
    model_version = relationship("ModelVersion", back_populates="predictions")
    feedback = relationship("UserFeedback", back_populates="prediction", uselist=False)

class TranslationHistory(Base):
    __tablename__ = "translation_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    session_id = Column(String(36), ForeignKey("recognition_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_tokens = Column(Text, nullable=False)
    translated_sentence = Column(Text, nullable=False)
    was_edited = Column(Boolean, default=False, nullable=False)
    edited_sentence = Column(Text, nullable=True)
    language = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    session = relationship("RecognitionSession", back_populates="translations")

class UserFeedback(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    prediction_id = Column(String(36), ForeignKey("recognition_predictions.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    true_label = Column(String(50), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    prediction = relationship("RecognitionPrediction", back_populates="feedback")
    user = relationship("User", back_populates="feedback")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="audit_logs")
