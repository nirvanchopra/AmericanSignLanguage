from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from app.core.database import get_db
from app.db.repositories.session_repo import AnalyticsRepository
from app.api.deps import get_current_user, get_current_admin
from app.db.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics & Model Metrics"])

@router.get("/dashboard")
async def get_user_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns user-level analytics: total sessions, total signs, average confidence, latency, and top signs.
    """
    repo = AnalyticsRepository(db)
    return await repo.get_user_dashboard_stats(user_id=current_user.id)

@router.get("/system")
async def get_system_analytics(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Administrative overview: active models, benchmark accuracy, system-wide sessions, and latency metrics.
    """
    repo = AnalyticsRepository(db)
    return await repo.get_system_analytics()
