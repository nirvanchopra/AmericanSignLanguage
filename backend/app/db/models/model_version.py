import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    model_name = Column(String(100), nullable=False)
    version_tag = Column(String(50), nullable=False, unique=True)
    framework = Column(String(50), nullable=False)  # onnx, pytorch, keras, mediapipe
    model_type = Column(String(50), nullable=False)  # static_alphabet, dynamic_words, hybrid
    classes = Column(JSON, nullable=False)  # list of recognizable class labels
    input_shape = Column(JSON, nullable=False)
    test_accuracy = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    deployed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    predictions = relationship("RecognitionPrediction", back_populates="model_version")
