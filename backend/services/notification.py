"""Реальный сервис уведомлений с интеграцией Telegram Bot API."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot
from telegram.error import BadRequest, Forbidden, NetworkError, TelegramError, TimedOut

from backend.crud import notification_crud, telegram_user_crud
from backend.schemas.admin.notification import (
    AdminNotificationListResponse,
    AdminNotificationRequest,
    AdminNotificationResponse,
    AdminNotificationUpdate,
)
from backend.validators.notification import notification_validator


class NotificationService:
    """Реальный сервис уведомлений с интеграцией Telegram Bot API."""

    def __init__(self):
        """Инициализация сервиса с Telegram Bot."""
        self.bot_token = os.getenv("BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("BOT_TOKEN не найден в переменных окружения")

        # Инициализируем бота для отправки уведомлений
        self.bot = Bot(token=self.bot_token)
        self.validator = notification_validator

    async def find_inactive_users(self, db: AsyncSession, inactive_days: int = 10) -> List:
        """Найти неактивных пользователей."""
        return await telegram_user_crud.get_inactive_users(db, inactive_days)

    async def create_reminder_notifications(self, db: AsyncSession, users: List) -> int:
        """Создать напоминания для пользователей с использованием активных шаблонов."""
        from backend.services.reminder_template import reminder_template_service

        # Получаем активный шаблон по умолчанию
        template = await reminder_template_service.get_default_template(db)

        count = 0
        for user in users:
            if template:
                # Используем шаблон с персонализацией
                message = reminder_template_service.personalize_message(template.message_template, user.first_name)
                await notification_crud.create_notification(
                    db=db, telegram_user_id=user.id, message=message, template_id=template.id
                )
            else:
                # Fallback сообщение если шаблонов нет
                message = f"Привет, {user.first_name}! Мы по вам соскучились! 🥰"
                await notification_crud.create_notification(db=db, telegram_user_id=user.id, message=message)
            count += 1
        return count

    async def send_pending_notifications(self, db: AsyncSession) -> dict:
        """Отправить все ожидающие уведомления."""
        notifications = await notification_crud.get_pending_notifications(db)

        sent = 0
        failed = 0

        for notification in notifications:
            try:
                # Реальная отправка в Telegram
                success = await self._send_telegram_message(notification.telegram_user_id, notification.message)

                if success:
                    await notification_crud.mark_as_sent(db, notification.id)
                    sent += 1
                else:
                    await notification_crud.mark_as_failed(db, notification.id)
                    failed += 1

            except Exception:
                await notification_crud.mark_as_failed(db, notification.id)
                failed += 1

        return {"total": len(notifications), "sent": sent, "failed": failed}

    async def _send_telegram_message(self, telegram_user_id: int, message: str) -> bool:
        """Реальная отправка сообщения пользователю через Telegram Bot API.

        Args:
            telegram_user_id: ID пользователя в Telegram
            message: Текст сообщения для отправки

        Returns:
            bool: True если сообщение отправлено успешно, False в случае ошибки
        """
        try:
            await self.bot.send_message(chat_id=telegram_user_id, text=message, parse_mode="HTML")
            print(f"✅ Уведомление успешно отправлено пользователю {telegram_user_id}")
            return True

        except BadRequest as e:
            print(f"❌ Ошибка запроса при отправке {telegram_user_id}: {e}")
            return False

        except Forbidden as e:
            print(f"❌ Пользователь {telegram_user_id} заблокировал бота: {e}")
            return False

        except NetworkError as e:
            print(f"❌ Сетевая ошибка при отправке {telegram_user_id}: {e}")
            return False

        except TimedOut as e:
            print(f"❌ Таймаут при отправке {telegram_user_id}: {e}")
            return False

        except Forbidden:
            print(f"❌ Неверный токен бота для отправки {telegram_user_id}")
            return False

        except TelegramError as e:
            print(f"❌ Общая ошибка Telegram при отправке {telegram_user_id}: {e}")
            return False

        except Exception as e:
            print(f"❌ Неожиданная ошибка при отправке {telegram_user_id}: {e}")
            return False

    async def send_admin_notification(
        self, db: AsyncSession, request: AdminNotificationRequest
    ) -> AdminNotificationResponse:
        """Отправить админское уведомление пользователю."""
        user = await telegram_user_crud.get_by_telegram_id(db, request.telegram_user_id)
        self.validator.validate_user_exists_for_id(user, request.telegram_user_id)

        notification = await notification_crud.create_notification(
            db=db,
            telegram_user_id=user.id,
            message=request.message,
        )

        # Реальная отправка через Telegram Bot API
        success = await self._send_telegram_message(user.telegram_id, request.message)

        if success:
            await notification_crud.mark_as_sent(db, notification.id)
            await telegram_user_crud.update_reminder_sent_status(db, user.id)

        return AdminNotificationResponse.model_validate(notification)

    async def get_admin_notifications(
        self, db: AsyncSession, days_ago: Optional[int] = None
    ) -> AdminNotificationListResponse:
        """Получить статистику уведомлений для админов."""
        start_date = None
        if days_ago:
            start_date = datetime.now(timezone.utc) - timedelta(days=days_ago)

        stats = await notification_crud.get_notification_statistics(db, start_date)

        return AdminNotificationListResponse(
            total_notifications=stats["total"],
            sent_notifications=stats["sent"],
            failed_notifications=stats["failed"],
            pending_notifications=stats["pending"],
            success_rate=stats["success_rate"],
        )

    async def update_admin_notification(
        self, db: AsyncSession, notification_id: int, request: AdminNotificationUpdate
    ) -> AdminNotificationResponse:
        """Обновить админское уведомление."""
        notification = await notification_crud.get(db, notification_id)
        self.validator.validate_notification_exists_for_id(notification, notification_id)

        # Обновляем статус
        if request.status == "sent":
            await notification_crud.mark_as_sent(db, notification_id)
        elif request.status == "failed":
            await notification_crud.mark_as_failed(db, notification_id)

        updated_notification = await notification_crud.get(db, notification_id)
        return AdminNotificationResponse.model_validate(updated_notification)


notification_service = NotificationService()
