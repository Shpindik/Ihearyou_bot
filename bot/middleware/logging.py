"""Middleware для логирования действий пользователей."""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from ..utils.api_client import APIClientError, api_client


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования действий пользователей."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Логирует активности пользователей."""
        # Получаем пользователя из события
        user = data.get("user")
        telegram_user_id = data.get("telegram_user_id")

        if not user:
            return await handler(event, data)

        try:
            # Определяем тип активности
            activity_type = await self._determine_activity_type(event, data)

            # Записываем активность в API
            if activity_type:
                await self._log_user_activity(telegram_user_id, activity_type, event, data)

        except Exception as e:
            logger.error(f"Error logging user activity: {e}")
            # Не прерываем обработку при ошибках логирования

        return await handler(event, data)

    async def _determine_activity_type(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        """Определяет тип активности пользователя."""
        if isinstance(event, Message):
            if event.text:
                if event.text.startswith("/start"):
                    return "start_command"
                elif event.text.startswith("/"):
                    return "navigation"
                else:
                    # Это может быть текстовый поисковый запрос
                    return "search"

        elif isinstance(event, CallbackQuery):
            callback_data = event.data

            if callback_data == "start_command":
                return "start_command"
            elif callback_data.startswith("menu_"):
                return "navigation"
            elif callback_data.startswith("search"):
                return "search"
            elif callback_data.startswith("ask_question"):
                return "question_ask"
            elif callback_data.startswith("rate_"):
                return "rating"
            elif callback_data.startswith("content_"):
                return "content_view"

        return None

    async def _log_user_activity(
        self, telegram_user_id: int, activity_type: str, event: TelegramObject, data: Dict[str, Any]
    ):
        """Логирует активность пользователя в API."""
        try:
            # Определяем дополнительные данные активности
            search_query = None
            menu_item_id = None

            if isinstance(event, Message) and event.text and not event.text.startswith("/"):
                # Проверяем на мусорные поисковые запросы
                if not self._is_spam_search(event.text.strip()):
                    search_query = event.text
                else:
                    # Пропускаем логирование мусорного поиска
                    logger.debug(f"Skipped spam search query: '{event.text}'")
                    return
            elif isinstance(event, CallbackQuery):
                callback_data = event.data

                if callback_data.startswith("menu_"):
                    # Извлекаем ID пункта меню
                    try:
                        menu_item_id = int(callback_data.split("_")[1])
                    except (IndexError, ValueError):
                        pass

                elif callback_data.startswith("search"):
                    # Извлекаем поисковый запрос если есть
                    if ":" in callback_data:
                        search_query = callback_data.split(":", 1)[1]

            # Формируем данные для API
            activity_data = {
                "telegram_user_id": telegram_user_id,
                "activity_type": activity_type,
                "search_query": search_query,
                "menu_item_id": menu_item_id,
            }

            async with api_client as client:
                response = await client._make_request(
                    method="POST", endpoint="api/v1/public/user-activities/", data=activity_data
                )

                logger.debug(f"Logged activity for user {telegram_user_id}: {response}")

        except APIClientError as e:
            logger.warning(f"API error logging activity for user {telegram_user_id}: {e}")

        except Exception as e:
            logger.error(f"Unexpected error logging activity for user {telegram_user_id}: {e}")
            raise

    def _is_spam_search(self, text: str) -> bool:
        """Проверяет является ли текст мусорным поисковым запросом.
        
        Args:
            text: Текст сообщения
            
        Returns:
            True если текст спам
        """
        if not text:
            return True
            
        text_lower = text.lower().strip()
        
        # Черный список мусорных запросов
        spam_patterns = {
            "привет", "hello", "hi", "здравствуйте", "как дела", "как у тебя",
            "что", "где", "когда", "почему", "как", "кто", "какой", "какая",
            "тест", "test", "проверка", "работает", "бот", "помощь", "хелп"
        }
        
        # Проверяем на прямые совпадения
        if text_lower in spam_patterns:
            return True
            
        # Слишком короткие запросы
        if len(text_lower) < 3:
            return True
            
        # Только повторяющиеся символы
        unique_chars = len(set(text_lower.replace(" ", "")))
        if unique_chars < 2:
            return True
            
        return False
