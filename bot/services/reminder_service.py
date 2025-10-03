"""Сервис автоматических напоминаний."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from aiogram import Bot

from ..config import settings
from ..utils.api_client import APIClientError, api_client


logger = logging.getLogger(__name__)


class ReminderService:
    """Сервис для отправки автоматических напоминаний неактивным пользователям."""

    def __init__(self, bot: Bot):
        """Инициализация сервиса напоминаний.

        Args:
            bot: Экземпляр Telegram бота
        """
        self.bot = bot
        self.is_running = False

    async def start(self):
        """Запускает службу напоминаний."""
        if self.is_running:
            logger.warning("Сервис напоминаний уже запущен")
            return

        self.is_running = True
        logger.info("Запуск сервиса автоматических напоминаний")

        # Запускаем фоновую задачу
        asyncio.create_task(self._reminder_loop())

    async def stop(self):
        """Останавливает службу напоминаний."""
        if not self.is_running:
            return

        self.is_running = False
        logger.info("Остановка сервиса автоматических напоминаний")

    async def _reminder_loop(self):
        """Основной цикл отправки напоминаний."""
        while self.is_running:
            try:
                await self._send_reminders()

                # Ждем до следующего запуска (каждые 12 часов)
                await asyncio.sleep(12 * 3600)

            except Exception as e:
                logger.error(f"Ошибка в цикле напоминаний: {e}")
                # Ждем час перед повтором при ошибке
                await asyncio.sleep(3600)

    async def _send_reminders(self):
        """Отправляет напоминания неактивным пользователям."""
        try:
            logger.info("Отправка напоминаний неактивным пользователям...")

            # Получаем список неактивных пользователей
            inactive_users = await self._get_inactive_users()

            if not inactive_users:
                logger.info("Нет неактивных пользователей для отправки напоминаний")
                return

            logger.info(f"Найдено {len(inactive_users)} неактивных пользователей")

            # Получаем активный шаблон сообщения
            template = await self._get_active_template()

            if not template:
                logger.warning("Нет активного шаблона для напоминаний")
                return

            # Отправляем напоминания
            sent_count = 0
            failed_count = 0

            for user in inactive_users:
                try:
                    success = await self._send_reminder_to_user(user, template)

                    if success:
                        # Обновляем статус отправки напоминания
                        await self._update_reminder_status(user["telegram_id"])
                        sent_count += 1
                    else:
                        failed_count += 1

                except Exception as e:
                    logger.error(f"Ошибка отправки напоминания пользователю {user['telegram_id']}: {e}")
                    failed_count += 1

                # Небольшая задержка между отправками
                await asyncio.sleep(0.5)

            logger.info(f"Отправка напоминаний завершена. " f"Успешно: {sent_count}, Ошибок: {failed_count}")

        except Exception as e:
            logger.error(f"Ошибка при отправке напоминаний: {e}")

    async def _get_inactive_users(self) -> List[Dict[str, Any]]:
        """Получает список неактивных пользователей."""
        try:
            params = {
                "inactive_days": settings.inactive_days_threshold,
                "days_since_last_reminder": settings.reminder_cooldown_days,
            }

            async with api_client as client:
                response = await client._make_request(
                    method="GET", endpoint="api/v1/bot/telegram-user/inactive-users", params=params
                )

                return response

        except APIClientError as e:
            logger.error(f"API error getting inactive users: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting inactive users: {e}")
            return []

    async def _get_active_template(self) -> Optional[Dict[str, Any]]:
        """Получает активный шаблон сообщения."""
        try:
            async with api_client as client:
                response = await client._make_request(
                    method="GET", endpoint="api/v1/bot/message-template/active-template"
                )

                return response

        except APIClientError as e:
            logger.error(f"API error getting active template: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting active template: {e}")
            return None

    async def _send_reminder_to_user(self, user: Dict[str, Any], template: Dict[str, Any]) -> bool:
        """Отправляет напоминание пользователю.

        Args:
            user: Данные пользователя
            template: Шаблон сообщения

        Returns:
            True если напоминание отправлено успешно
        """
        try:
            telegram_id = user["telegram_id"]
            first_name = user.get("first_name", "Пользователь")

            # Персонализируем сообщение
            message_text = template["message_template"].replace("{first_name}", first_name)

            # Отправляем сообщение
            await self.bot.send_message(
                chat_id=telegram_id,
                text=message_text,
                parse_mode=settings.parse_mode,
                disable_web_page_preview=settings.disable_web_page_preview,
            )

            logger.info(f"Напоминание отправлено пользователю {telegram_id}")
            return True

        except Exception as e:
            logger.error(f"Ошибка отправки напоминания пользователю {user.get('telegram_id')}: {e}")
            return False

    async def _update_reminder_status(self, telegram_user_id: int) -> bool:
        """Обновляет статус отправки напоминания."""
        try:
            async with api_client as client:
                await client._make_request(
                    method="POST",
                    endpoint="api/v1/bot/telegram-user/update-reminder-status",
                    data={"telegram_user_id": telegram_user_id},
                )

                return True

        except APIClientError as e:
            logger.error(f"API error updating reminder status: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating reminder status: {e}")
            return False

    async def send_manual_reminder(self, telegram_user_id: int, message: str) -> bool:
        """Отправляет ручное напоминание пользователю.

        Args:
            telegram_user_id: ID пользователя в Telegram
            message: Текст сообщения

        Returns:
            True если напоминание отправлено успешно
        """
        try:
            await self.bot.send_message(
                chat_id=telegram_user_id,
                text=message,
                parse_mode=settings.parse_mode,
                disable_web_page_preview=settings.disable_web_page_preview,
            )

            logger.info(f"Ручное напоминание отправлено пользователю {telegram_user_id}")
            return True

        except Exception as e:
            logger.error(f"Ошибка отправки ручного напоминания: {e}")
            return False
