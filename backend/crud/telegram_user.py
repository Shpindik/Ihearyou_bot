"""CRUD операции для пользователей Telegram."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import TelegramUser

from .base import BaseCRUD


class TelegramUserCRUD(BaseCRUD[TelegramUser, dict, dict]):
    """CRUD операции для пользователей Telegram."""

    def __init__(self):
        """Инициализация CRUD для пользователей Telegram."""
        super().__init__(TelegramUser)

    async def get_by_telegram_id(
        self, db: AsyncSession, telegram_id: int
    ) -> Optional[TelegramUser]:
        """Получить пользователя по Telegram ID."""
        query = select(TelegramUser).where(TelegramUser.telegram_id == telegram_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        db: AsyncSession,
        telegram_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> TelegramUser:
        """Получить или создать пользователя."""
        user = await self.get_by_telegram_id(db, telegram_id)

        if user:
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.last_activity = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(user)
        else:
            user_data = {
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "last_activity": datetime.now(timezone.utc),
            }
            user = TelegramUser(**user_data)
            db.add(user)
            await db.commit()
            await db.refresh(user)

        return user

    async def update_activity(self, db: AsyncSession, telegram_id: int) -> None:
        """Обновить время последней активности."""
        user = await self.get_by_telegram_id(db, telegram_id)
        if user:
            user.last_activity = datetime.now(timezone.utc)
            await db.commit()


user_crud = TelegramUserCRUD()
