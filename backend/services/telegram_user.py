"""Сервис для работы с пользователями Telegram."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.telegram_user import telegram_user_crud
from backend.schemas.admin.telegram_user import AdminTelegramUserListResponse, AdminTelegramUserResponse
from backend.schemas.bot.telegram_user import (
    BotInactiveUserResponse,
    BotReminderStatusResponse,
    TelegramUserRequest,
    TelegramUserResponse,
)
from backend.validators.telegram_user import telegram_user_validator


class TelegramUserService:
    """Сервис для работы с пользователями Telegram."""

    def __init__(self):
        """Инициализация сервиса Telegram User."""
        self.telegram_user_crud = telegram_user_crud
        self.validator = telegram_user_validator

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
        self.validator.validate_telegram_id(telegram_id)

        existing_user = await self.telegram_user_crud.get_by_telegram_id(db, telegram_id)
        user_created = existing_user is None

        user = await self.telegram_user_crud.upsert_user(
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

    async def get_all_users(self, db: AsyncSession) -> AdminTelegramUserListResponse:
        """Получить всех пользователей для администраторов.

        Args:
            db: Сессия базы данных

        Returns:
            Список всех пользователей с базовой статистикой
        """
        users = await self.telegram_user_crud.get_all_users(db)

        items = []
        for user in users:
            # Используем агрегационные поля из модели вместо отдельных запросов
            item = AdminTelegramUserResponse(
                id=user.id,
                telegram_id=user.telegram_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                subscription_type=user.subscription_type,
                last_activity=user.last_activity,
                reminder_sent_at=user.reminder_sent_at,
                created_at=user.created_at,
                activities_count=user.activities_count,
                questions_count=user.questions_count,
            )
            items.append(item)

        return AdminTelegramUserListResponse(items=items)

    async def get_user_by_id(self, user_id: int, db: AsyncSession) -> AdminTelegramUserResponse:
        """Получить пользователя по ID с полной статистикой.

        Args:
            user_id: ID пользователя
            db: Сессия базы данных

        Returns:
            Детальная информация о пользователе
        """
        user = await self.telegram_user_crud.get(db, user_id)
        self.validator.validate_user_exists(user)

        # Используем агрегационные поля из модели
        return AdminTelegramUserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            subscription_type=user.subscription_type,
            last_activity=user.last_activity,
            reminder_sent_at=user.reminder_sent_at,
            created_at=user.created_at,
            activities_count=user.activities_count,
            questions_count=user.questions_count,
        )

    async def update_user_activity(self, db: AsyncSession, telegram_id: int) -> None:
        """Обновить время последней активности пользователя - бизнес-логика в сервисе.

        Args:
            db: Сессия базы данных
            telegram_id: Telegram ID пользователя
        """
        from datetime import datetime, timezone

        current_time = datetime.now(timezone.utc)
        await self.telegram_user_crud.update_last_activity(db=db, telegram_id=telegram_id, last_activity=current_time)

    async def increment_user_activities_count(
        self, db: AsyncSession, telegram_user_id: int, increment: int = 1
    ) -> None:
        """Увеличить счетчик активностей пользователя - бизнес-логика в сервисе.

        Args:
            db: Сессия базы данных
            telegram_user_id: ID пользователя в БД
            increment: Шаг увеличения
        """
        await self.telegram_user_crud.increment_activities_count(
            db=db, telegram_user_id=telegram_user_id, increment=increment
        )

    async def increment_user_questions_count(self, db: AsyncSession, telegram_user_id: int, increment: int = 1) -> None:
        """Увеличить счетчик вопросов пользователя - бизнес-логика в сервисе.

        Args:
            db: Сессия базы данных
            telegram_user_id: ID пользователя в БД
            increment: Шаг увеличения
        """
        await self.telegram_user_crud.increment_questions_count(
            db=db, telegram_user_id=telegram_user_id, increment=increment
        )

    async def get_inactive_users(
        self, db: AsyncSession, inactive_days: int, days_since_last_reminder: int
    ) -> list[BotInactiveUserResponse]:
        """Получить неактивных пользователей для напоминаний.

        Args:
            db: Сессия базы данных
            inactive_days: Дни неактивности
            days_since_last_reminder: Дни с последнего напоминания

        Returns:
            Список неактивных пользователей для напоминаний
        """
        inactive_users = await self.telegram_user_crud.get_inactive_users(
            db=db, inactive_days=inactive_days, days_since_last_reminder=days_since_last_reminder
        )

        return [
            BotInactiveUserResponse(
                telegram_user_id=user.telegram_id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                last_activity=user.last_activity.isoformat() if user.last_activity else None,
                reminder_sent_at=user.reminder_sent_at.isoformat() if user.reminder_sent_at else None,
            )
            for user in inactive_users
        ]

    async def update_reminder_status(self, db: AsyncSession, telegram_user_id: int) -> BotReminderStatusResponse:
        """Обновить статус отправки напоминания пользователю.

        Args:
            db: Сессия базы данных
            telegram_user_id: Telegram ID пользователя

        Returns:
            Ответ с результатом обновления статуса
        """
        from datetime import datetime, timezone

        user = await self.telegram_user_crud.get_by_telegram_id(db, telegram_user_id)
        self.validator.validate_user_exists(user)

        await self.telegram_user_crud.update_reminder_sent_status(db, telegram_user_id=user.id)

        return BotReminderStatusResponse(
            success="true",
            message=f"Статус напоминания обновлен для пользователя {user.first_name}",
            reminder_sent_at=datetime.now(timezone.utc).isoformat(),
        )


telegram_user_service = TelegramUserService()
