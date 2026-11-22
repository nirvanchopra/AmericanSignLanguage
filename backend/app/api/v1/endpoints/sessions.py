from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.db.repositories.session_repo import SessionRepository
from app.api.v1.schemas import SessionCreate, SessionOut
from app.api.deps import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    data: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = SessionRepository(db)
    session = await repo.create(
        user_id=current_user.id,
        session_name=data.session_name,
        session_type=data.session_type,
        total_signs_recognized=0,
        average_confidence=0.0,
        duration_seconds=0
    )
    return session

@router.get("/", response_model=List[SessionOut])
async def list_user_sessions(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = SessionRepository(db)
    return await repo.get_user_sessions(user_id=current_user.id, limit=limit)

@router.get("/{session_id}")
async def get_session_detail(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = SessionRepository(db)
    session = await repo.get_session_detail(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    
    return {
        "id": session.id,
        "session_name": session.session_name,
        "session_type": session.session_type,
        "total_signs": session.total_signs_recognized,
        "average_confidence": session.average_confidence,
        "duration_seconds": session.duration_seconds,
        "created_at": session.created_at,
        "ended_at": session.ended_at,
        "predictions": [
            {
                "id": p.id,
                "label": p.predicted_label,
                "confidence": p.confidence,
                "top3": p.top3_alternatives,
                "latency_ms": p.inference_latency_ms,
                "timestamp": p.timestamp
            }
            for p in session.predictions
        ],
        "translations": [
            {
                "id": t.id,
                "raw_tokens": t.raw_tokens,
                "sentence": t.translated_sentence,
                "edited_sentence": t.edited_sentence,
                "created_at": t.created_at
            }
            for t in session.translations
        ]
    }

@router.post("/{session_id}/end", response_model=SessionOut)
async def end_session(
    session_id: str,
    duration_seconds: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = SessionRepository(db)
    session = await repo.get_by_id(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    
    updated = await repo.update(
        session_id,
        ended_at=datetime.utcnow(),
        duration_seconds=duration_seconds
    )
    return updated
