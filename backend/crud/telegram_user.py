"""CRUD операции для пользователей Telegram."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import TelegramUser

from .base import BaseCRUD


class TelegramUserCRUD(BaseCRUD[TelegramUser, dict, dict]):
    """CRUD операции для пользователей Telegram."""

    def __init__(self):
        """Инициализация CRUD для пользователей Telegram."""
        super().__init__(TelegramUser)

    async def get_by_telegram_id(self, db: AsyncSession, telegram_id: int) -> Optional[TelegramUser]:
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
        """Получить или создать пользователя с использованием UPSERT для атомарности."""
        current_time = datetime.now(timezone.utc)

        stmt = pg_insert(TelegramUser).values(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            last_activity=current_time,
            created_at=current_time,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["telegram_id"],
            set_={
                "first_name": stmt.excluded.first_name,
                "last_name": stmt.excluded.last_name,
                "username": stmt.excluded.username,
                "last_activity": stmt.excluded.last_activity,
            },
        )

        stmt = stmt.returning(TelegramUser)

        result = await db.execute(stmt)
        user = result.scalar_one()

        await db.commit()
        await db.refresh(user)
        print(user)

        return user

    async def update_activity(self, db: AsyncSession, telegram_id: int) -> None:
        """Обновить время последней активности с использованием транзакции."""
        current_time = datetime.now(timezone.utc)

        stmt = update(TelegramUser).where(TelegramUser.telegram_id == telegram_id).values(last_activity=current_time)

        await db.execute(stmt)
        await db.commit()

    async def get_inactive(self, db: AsyncSession, days: int = 10) -> List[TelegramUser]:
        """Получение списка неактивных пользователей."""
        threshold = datetime.now(timezone.utc) - timedelta(days=days)

        query = select(TelegramUser).where(
            TelegramUser.last_activity < threshold, TelegramUser.reminder_sent_at < threshold
        )
        # gives all users for testing
        query = select(TelegramUser)
        result = await db.execute(query)
        items = result.scalars().all()
        return items


telegram_user_crud = TelegramUserCRUD()
