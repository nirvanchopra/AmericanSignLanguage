from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models.user import User, UserProfile
from app.db.repositories.base_repo import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).options(selectinload(User.profile)).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_profile(self, user_id: str) -> Optional[User]:
        stmt = select(User).options(selectinload(User.profile)).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_profile(self, user_id: str, **kwargs) -> Optional[UserProfile]:
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.db.execute(stmt)
        profile = result.scalar_one_or_none()
        if not profile:
            profile = UserProfile(user_id=user_id, **kwargs)
            self.db.add(profile)
        else:
            for key, value in kwargs.items():
                if hasattr(profile, key) and value is not None:
                    setattr(profile, key, value)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
