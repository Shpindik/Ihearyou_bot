"""Сервис для работы с пользователями Telegram."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import telegram_user_crud
from backend.schemas.bot.telegram_user import TelegramUserRequest, TelegramUserResponse
from backend.validators import telegram_user_validator


class TelegramUserService:
    """Сервис для работы с пользователями Telegram."""

    def __init__(self):
        """Инициализация сервиса Telegram User."""

    async def register_user(self, request: TelegramUserRequest, db: AsyncSession) -> TelegramUserResponse:
        """Регистрация пользователя Telegram в системе.

        Args:
            request: Данные пользователя от бота
            db: Сессия базы данных

        Returns:
            Ответ с данными пользователя и статусом обработки
        """
        if request.message:
            user_data = request.message.get("from")
        elif request.callback_query:
            user_data = request.callback_query.get("from")
        else:
            user_data = None

        telegram_id = user_data.get("id") if user_data else None
        telegram_user_validator.validate_telegram_id(telegram_id)

        existing_user = await telegram_user_crud.get_by_telegram_id(db, telegram_id)
        user_created = existing_user is None

        user = await telegram_user_crud.get_or_create(
            db=db,
            telegram_id=telegram_id,
            first_name=user_data.get("first_name") if user_data else None,
            last_name=user_data.get("last_name") if user_data else None,
            username=user_data.get("username") if user_data else None,
        )

        # Создаем словарь с данными пользователя для сериализации
        user_data = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "subscription_type": user.subscription_type,
            "last_activity": user.last_activity,
            "reminder_sent_at": user.reminder_sent_at,
            "created_at": user.created_at,
        }

        return TelegramUserResponse(
            user=user_data,
            message_processed=True,
            user_created=user_created,
            user_updated=not user_created,
        )


telegram_user_service = TelegramUserService()
