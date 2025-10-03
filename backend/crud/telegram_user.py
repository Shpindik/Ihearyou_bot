"""CRUD операции для пользователей Telegram."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import and_, func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import TelegramUser, UserActivity, UserQuestion
from backend.models.enums import SubscriptionType

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

    async def upsert_user(
        self,
        db: AsyncSession,
        *,
        telegram_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> TelegramUser:
        """Получить или создать пользователя.

        Args:
            db: Сессия базы данных
            telegram_id: Telegram ID пользователя
            first_name: Имя пользователя
            last_name: Фамилия пользователя (опционально)
            username: Username пользователя (опционально)
        """
        current_time = datetime.now(timezone.utc)

        stmt = pg_insert(TelegramUser).values(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            subscription_type=SubscriptionType.FREE,
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

        return user

    async def update_last_activity(self, db: AsyncSession, *, telegram_id: int, last_activity: datetime) -> None:
        """Обновить время последней активности."""
        stmt = update(TelegramUser).where(TelegramUser.telegram_id == telegram_id).values(last_activity=last_activity)

        await db.execute(stmt)
        await db.commit()

    async def get_all_users(self, db: AsyncSession) -> List[TelegramUser]:
        """Получить всех пользователей для админского интерфейса."""
        query = select(TelegramUser).order_by(TelegramUser.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def count_user_activities(self, db: AsyncSession, telegram_user_id: int) -> int:
        """Подсчитать количество активностей пользователя."""
        query = select(func.count(UserActivity.id)).where(UserActivity.telegram_user_id == telegram_user_id)
        result = await db.execute(query)
        return result.scalar() or 0

    async def count_user_questions(self, db: AsyncSession, telegram_user_id: int) -> int:
        """Подсчитать количество вопросов пользователя."""
        query = select(func.count(UserQuestion.id)).where(UserQuestion.telegram_user_id == telegram_user_id)
        result = await db.execute(query)
        return result.scalar()

    async def increment_activities_count(self, db: AsyncSession, *, telegram_user_id: int, increment: int = 1) -> None:
        """Увеличить счетчик активностей пользователя."""
        await db.execute(
            update(TelegramUser)
            .where(TelegramUser.id == telegram_user_id)
            .values(activities_count=TelegramUser.activities_count + increment)
        )
        await db.commit()

    async def increment_questions_count(self, db: AsyncSession, *, telegram_user_id: int, increment: int = 1) -> None:
        """Увеличить счетчик вопросов пользователя."""
        await db.execute(
            update(TelegramUser)
            .where(TelegramUser.id == telegram_user_id)
            .values(questions_count=TelegramUser.questions_count + increment)
        )
        await db.commit()

    async def get_inactive_users(
        self, db: AsyncSession, inactive_days: int = 10, days_since_last_reminder: int = 10
    ) -> List[TelegramUser]:
        """Получить список неактивных пользователей для отправки напоминаний.

        Args:
            db: Сессия базы данных
            inactive_days: Количество дней неактивности (по умолчанию 10)
            days_since_last_reminder: Минимальные дни между напоминаниями (по умолчанию 10)

        Returns:
            Список пользователей, которым нужно отправить напоминание
        """
        current_time = datetime.now(timezone.utc)
        inactive_threshold = current_time - timedelta(days=inactive_days)
        reminder_threshold = current_time - timedelta(days=days_since_last_reminder)

        query = (
            select(TelegramUser)
            .where(
                and_(
                    TelegramUser.last_activity < inactive_threshold,
                    (TelegramUser.reminder_sent_at < reminder_threshold) | (TelegramUser.reminder_sent_at.is_(None)),
                    TelegramUser.created_at < inactive_threshold,
                )
            )
            .order_by(TelegramUser.last_activity.asc())
        )

        result = await db.execute(query)
        return result.scalars().all()

    async def update_reminder_sent_status(
        self, db: AsyncSession, *, telegram_user_id: int, sent_at: Optional[datetime] = None
    ) -> None:
        """Обновить статус отправки напоминания пользователю.

        Args:
            db: Сессия базы данных
            telegram_user_id: ID пользователя Telegram
            sent_at: Время отправки (по умолчанию сейчас)
        """
        if sent_at is None:
            sent_at = datetime.now(timezone.utc)

        await db.execute(
            update(TelegramUser).where(TelegramUser.id == telegram_user_id).values(reminder_sent_at=sent_at)
        )
        await db.commit()


telegram_user_crud = TelegramUserCRUD()
