"""Middleware для автоматической регистрации пользователей."""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from ..utils.api_client import APIClientError, api_client


logger = logging.getLogger(__name__)


class UserRegistrationMiddleware(BaseMiddleware):
    """Middleware для автоматической регистрации пользователей в API."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Обрабатывает входящие обновления и регистрирует пользователей."""
        # Получаем пользователя из события
        user = getattr(event, "from_user", None)

        if not user:
            return await handler(event, data)

        try:
            # Регистрируем/обновляем пользователя в API
            await self._register_user(user, event)

            # Добавляем информацию о пользователе в данные
            data["user"] = user
            data["telegram_user_id"] = user.id

        except Exception as e:
            logger.error(f"Error registering user {user.id}: {e}")
            # Продолжаем обработку даже при ошибке регистрации

        return await handler(event, data)

    async def _register_user(self, user, event):
        """Регистрирует/обновляет пользователя в API."""
        try:
            # Извлекаем данные пользователя
            telegram_user_id = user.id
            first_name = user.first_name or "Пользователь"
            last_name = user.last_name
            username = user.username

            # Создаем простой запрос для регистрации пользователя
            from aiogram.types import CallbackQuery, Message

            # Создаем корректный запрос согласно TelegramUserRequest схеме
            # Базовая структура согласно API схеме
            if isinstance(event, Message):
                registration_data = {
                    "update_id": event.chat.id,  # Используем chat_id как update_id
                    "message": {
                        "message_id": event.message_id,
                        "from": {
                            "id": telegram_user_id,
                            "first_name": first_name,
                            "last_name": last_name,
                            "username": username,
                        },
                        "chat": {
                            "id": event.chat.id,
                            "type": event.chat.type,
                        },
                        "date": event.date.timestamp() if event.date else None,
                        "text": event.text or "",
                    },
                    "callback_query": None,
                }
            elif isinstance(event, CallbackQuery):
                registration_data = {
                    "update_id": event.message.chat.id if event.message else telegram_user_id,
                    "message": None,
                    "callback_query": {
                        "id": str(event.id),
                        "from": {
                            "id": telegram_user_id,
                            "first_name": first_name,
                            "last_name": last_name,
                            "username": username,
                        },
                        "data": event.data or "",
                        "chat_instance": "" if event.message else "",
                    },
                }
            else:
                # Fallback для других типов событий
                registration_data = {
                    "update_id": telegram_user_id,
                    "message": {
                        "message_id": 1,
                        "from": {
                            "id": telegram_user_id,
                            "first_name": first_name,
                            "last_name": last_name,
                            "username": username,
                        },
                        "chat": {
                            "id": telegram_user_id,
                            "type": "private",
                        },
                        "date": None,
                        "text": "",
                    },
                    "callback_query": None,
                }

            async with api_client as client:
                response = await client._make_request(
                    method="POST", endpoint="api/v1/bot/telegram-user/register", data=registration_data
                )

                logger.debug(f"User {telegram_user_id} registration response: {response}")

        except APIClientError as e:
            logger.warning(f"API error registering user {user.id}: {e}")
            # Не прерываем обработку событий при ошибках API

        except Exception as e:
            logger.error(f"Unexpected error registering user {user.id}: {e}")
            raise
