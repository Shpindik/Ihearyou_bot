"""CRUD операции для активности пользователей."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseCRUD
from models import UserActivity
from models.enums import ActivityType


class UserActivityCRUD(BaseCRUD[UserActivity, dict, dict]):
    """CRUD операции для активности пользователей."""

    def __init__(self):
        super().__init__(UserActivity)

    async def create_activity(
        self, 
        db: AsyncSession,
        telegram_user_id: int,
        menu_item_id: int,
        activity_type: ActivityType,
        search_query: Optional[str] = None,
        rating: Optional[int] = None
    ) -> UserActivity:
        """Создать запись активности."""
        activity_data = {
            "telegram_user_id": telegram_user_id,
            "menu_item_id": menu_item_id,
            "activity_type": activity_type,
            "search_query": search_query,
            "rating": rating
        }
        
        activity = UserActivity(**activity_data)
        db.add(activity)
        await db.commit()
        await db.refresh(activity)
        return activity

    async def get_user_activities(
        self, 
        db: AsyncSession, 
        telegram_user_id: int,
        limit: int = 50
    ) -> List[UserActivity]:
        """Получить активность пользователя."""
        query = select(UserActivity).where(
            UserActivity.telegram_user_id == telegram_user_id
        ).order_by(UserActivity.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_menu_activities(
        self, 
        db: AsyncSession, 
        menu_item_id: int,
        limit: int = 100
    ) -> List[UserActivity]:
        """Получить активность по пункту меню."""
        query = select(UserActivity).where(
            UserActivity.menu_item_id == menu_item_id
        ).order_by(UserActivity.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()


activity_crud = UserActivityCRUD()
