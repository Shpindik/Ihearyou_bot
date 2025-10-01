"""Сервис для работы с напоминаниями."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import telegram_user_crud
from backend.schemas.bot.reminder import InactiveListUserResponse, InactiveUserResponse


class ReminderService:
    """Сервис для работы с напоминаниями."""

    def __init__(self):
        """Инициализация сервиса Reminder."""

    async def get_inactive_users(
        self,
        inactive_days: int,
        db: AsyncSession = None,
    ) -> InactiveListUserResponse:
        """Получение списка неактивных пользователей.

        Args:
            inactive_days: Количество неактивных дней
            db: Сессия базы данных

        Returns:
            Список пользователей
        """
        users = await telegram_user_crud.get_inactive(db=db, days=inactive_days)

        users_data = [InactiveUserResponse.model_validate(user) for user in users]
        return InactiveListUserResponse(users=users_data)


reminder_service = ReminderService()
