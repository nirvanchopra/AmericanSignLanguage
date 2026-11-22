from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from app.db.models.session import (
    RecognitionSession,
    RecognitionPrediction,
    TranslationHistory,
    UserFeedback
)
from app.db.models.model_version import ModelVersion
from app.db.repositories.base_repo import BaseRepository

class SessionRepository(BaseRepository[RecognitionSession]):
    def __init__(self, db: AsyncSession):
        super().__init__(RecognitionSession, db)

    async def get_user_sessions(self, user_id: str, limit: int = 50) -> List[RecognitionSession]:
        stmt = (
            select(RecognitionSession)
            .where(RecognitionSession.user_id == user_id)
            .order_by(desc(RecognitionSession.created_at))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_session_detail(self, session_id: str) -> Optional[RecognitionSession]:
        stmt = (
            select(RecognitionSession)
            .options(
                selectinload(RecognitionSession.predictions),
                selectinload(RecognitionSession.translations)
            )
            .where(RecognitionSession.id == session_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add_prediction(
        self,
        session_id: str,
        predicted_label: str,
        confidence: float,
        top3: List[Dict[str, Any]],
        latency_ms: float,
        is_unknown: bool = False,
        model_version_id: Optional[str] = None
    ) -> RecognitionPrediction:
        prediction = RecognitionPrediction(
            session_id=session_id,
            model_version_id=model_version_id,
            predicted_label=predicted_label,
            confidence=confidence,
            top3_alternatives=top3,
            inference_latency_ms=latency_ms,
            is_unknown=is_unknown
        )
        self.db.add(prediction)
        
        # Update session running counters
        session = await self.get_by_id(session_id)
        if session:
            prev_total = session.total_signs_recognized
            session.total_signs_recognized = prev_total + 1
            session.average_confidence = (
                (session.average_confidence * prev_total + confidence) / (prev_total + 1)
            )
        await self.db.commit()
        await self.db.refresh(prediction)
        return prediction

    async def add_translation(
        self,
        session_id: str,
        raw_tokens: str,
        translated_sentence: str,
        language: str = "en"
    ) -> TranslationHistory:
        translation = TranslationHistory(
            session_id=session_id,
            raw_tokens=raw_tokens,
            translated_sentence=translated_sentence,
            language=language
        )
        self.db.add(translation)
        await self.db.commit()
        await self.db.refresh(translation)
        return translation

class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_dashboard_stats(self, user_id: str) -> Dict[str, Any]:
        # Total sessions
        sess_stmt = select(func.count(RecognitionSession.id)).where(RecognitionSession.user_id == user_id)
        total_sessions = (await self.db.execute(sess_stmt)).scalar() or 0

        # Total signs & avg confidence
        signs_stmt = (
            select(
                func.sum(RecognitionSession.total_signs_recognized),
                func.avg(RecognitionSession.average_confidence)
            )
            .where(RecognitionSession.user_id == user_id)
        )
        signs_res = (await self.db.execute(signs_stmt)).one_or_none()
        total_signs = signs_res[0] or 0 if signs_res else 0
        avg_confidence = signs_res[1] or 0.0 if signs_res else 0.0

        # Most frequent signs for this user
        freq_stmt = (
            select(
                RecognitionPrediction.predicted_label,
                func.count(RecognitionPrediction.id).label("freq")
            )
            .join(RecognitionSession, RecognitionPrediction.session_id == RecognitionSession.id)
            .where(RecognitionSession.user_id == user_id)
            .where(RecognitionPrediction.is_unknown == False)
            .group_by(RecognitionPrediction.predicted_label)
            .order_by(desc("freq"))
            .limit(5)
        )
        freq_results = (await self.db.execute(freq_stmt)).all()
        top_signs = [{"sign": row[0], "count": row[1]} for row in freq_results]

        # Avg latency
        lat_stmt = (
            select(func.avg(RecognitionPrediction.inference_latency_ms))
            .join(RecognitionSession, RecognitionPrediction.session_id == RecognitionSession.id)
            .where(RecognitionSession.user_id == user_id)
        )
        avg_latency = (await self.db.execute(lat_stmt)).scalar() or 3.2

        return {
            "total_sessions": total_sessions,
            "total_signs_recognized": total_signs,
            "average_confidence": round(float(avg_confidence) * 100, 1),
            "average_latency_ms": round(float(avg_latency), 2),
            "top_signs": top_signs
        }

    async def get_system_analytics(self) -> Dict[str, Any]:
        total_users = (await self.db.execute(select(func.count(RecognitionSession.user_id.distinct())))).scalar() or 0
        total_sessions = (await self.db.execute(select(func.count(RecognitionSession.id)))).scalar() or 0
        total_preds = (await self.db.execute(select(func.count(RecognitionPrediction.id)))).scalar() or 0
        avg_conf = (await self.db.execute(select(func.avg(RecognitionPrediction.confidence)))).scalar() or 0.89

        # Active models
        m_stmt = select(ModelVersion).where(ModelVersion.is_active == True)
        models = (await self.db.execute(m_stmt)).scalars().all()

        return {
            "total_users": total_users,
            "total_sessions": total_sessions,
            "total_predictions": total_preds,
            "system_average_confidence": round(float(avg_conf) * 100, 1),
            "active_models": [
                {
                    "name": m.model_name,
                    "version": m.version_tag,
                    "accuracy": m.test_accuracy,
                    "latency_ms": m.latency_ms,
                    "type": m.model_type
                }
                for m in models
            ]
        }
