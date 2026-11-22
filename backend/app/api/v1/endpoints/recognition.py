from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from app.core.database import get_db
from app.ml.recognition_engine import recognition_engine
from app.api.v1.schemas import (
    RecognitionRequest,
    RecognitionResponse,
    FeedbackCreate,
    ModelVersionOut
)
from app.db.models.model_version import ModelVersion
from app.db.models.session import UserFeedback, RecognitionPrediction
from app.db.repositories.session_repo import SessionRepository
from app.api.deps import get_optional_user
from app.db.models.user import User

router = APIRouter(prefix="/recognition", tags=["Recognition Engine"])

@router.post("/recognize", response_model=RecognitionResponse)
async def recognize_landmarks(
    request: RecognitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """
    Real-time inference endpoint:
    Processes 21 MediaPipe hand landmarks with normalization, classification, and smoothing.
    """
    raw_landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in request.landmarks]

    result = recognition_engine.process_frame(
        landmarks=raw_landmarks,
        handedness=request.handedness,
        model_preference=request.model_preference,
        raw_pixel_points=request.raw_pixel_points,
        bbox=request.bbox
    )

    # If session_id provided, record prediction in database
    if request.session_id and result["is_new_token"] and not result["is_unknown"]:
        repo = SessionRepository(db)
        await repo.add_prediction(
            session_id=request.session_id,
            predicted_label=result["active_stable_label"],
            confidence=result["confidence"],
            top3=result["top3"],
            latency_ms=result["latency_ms"],
            is_unknown=result["is_unknown"]
        )

    return {
        "label": result["label"],
        "stabilized_label": result["stabilized_label"],
        "confidence": result["confidence"],
        "is_unknown": result["is_unknown"],
        "is_new_token": result["is_new_token"],
        "dynamic_word": result["dynamic_word"],
        "dynamic_confidence": result["dynamic_confidence"],
        "top3": result["top3"],
        "latency_ms": result["latency_ms"],
        "model_used": result["model_used"]
    }

@router.get("/models", response_model=List[ModelVersionOut])
async def list_models(db: AsyncSession = Depends(get_db)):
    """
    Returns metadata on all active model versions (LandmarkNet, BiLSTM, Legacy H5).
    """
    stmt = select(ModelVersion).where(ModelVersion.is_active == True)
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    data: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """
    Records human-in-the-loop validation feedback for accuracy auditing.
    """
    user_id = current_user.id if current_user else None
    feedback = UserFeedback(
        prediction_id=data.prediction_id,
        user_id=user_id,
        true_label=data.true_label,
        is_correct=data.is_correct,
        comment=data.comment
    )
    db.add(feedback)
    await db.commit()
    return {"status": "success", "message": "Feedback recorded successfully."}

@router.post("/reset")
async def reset_recognition_state():
    """
    Clears moving averages, hysteresis state, and temporal sequence buffers.
    """
    recognition_engine.reset_state()
    return {"status": "success", "message": "Recognition engine state reset."}
