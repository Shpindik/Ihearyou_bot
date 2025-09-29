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
            user_data = request.message["from"]
        elif request.callback_query:
            user_data = request.callback_query["from"]
        else:
            user_data = None

        telegram_user_validator.validate_telegram_id(user_data["id"] if user_data else None)

        existing_user = await telegram_user_crud.get_by_telegram_id(db, user_data["id"] if user_data else None)
        user_created = existing_user is None

        async with db.begin():
            user = await telegram_user_crud.get_or_create(
                db=db,
                telegram_id=user_data["id"] if user_data else None,
                first_name=user_data["first_name"] if user_data else None,
                last_name=user_data.get("last_name") if user_data else None,
                username=user_data.get("username") if user_data else None,
            )

        return self._build_user_response(user, user_created)

    def _build_user_response(self, user, user_created: bool) -> TelegramUserResponse:
        """Формирование ответа регистрации пользователя.

        Args:
            user: Объект пользователя из базы данных
            user_created: Флаг создания нового пользователя

        Returns:
            Ответ с данными пользователя
        """
        return TelegramUserResponse(
            user={
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "subscription_type": user.subscription_type,
                "last_activity": user.last_activity.isoformat() if user.last_activity else None,
                "reminder_sent_at": user.reminder_sent_at.isoformat() if user.reminder_sent_at else None,
                "created_at": user.created_at.isoformat(),
            },
            message_processed=True,
            user_created=user_created,
            user_updated=not user_created,
        )


telegram_user_service = TelegramUserService()
