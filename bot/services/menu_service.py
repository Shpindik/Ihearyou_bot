"""Сервис для работы с меню и навигацией."""

import logging
from typing import Any, Dict, List, Optional

from ..utils.api_client import APIClientError, api_client


logger = logging.getLogger(__name__)


class MenuService:
    """Сервис для работы с меню и навигацией."""

    async def get_menu_items(self, telegram_user_id: int, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Получает пункты меню для пользователя.

        Args:
            telegram_user_id: ID пользователя в Telegram
            parent_id: ID родительского пункта меню (None для корневого уровня)

        Returns:
            Список пунктов меню
        """
        try:
            params = {"telegram_user_id": telegram_user_id}
            if parent_id is not None:
                params["parent_id"] = parent_id

            async with api_client as client:
                response = await client._make_request(method="GET", endpoint="api/v1/public/menu-items/", params=params)

                return response.get("items", [])

        except APIClientError as e:
            logger.error(f"API error getting menu items: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting menu items: {e}")
            raise

    async def get_menu_content(self, telegram_user_id: int, menu_item_id: int) -> Optional[Dict[str, Any]]:
        """Получает контент пункта меню.

        Args:
            telegram_user_id: ID пользователя в Telegram
            menu_item_id: ID пункта меню

        Returns:
            Данные контента или None если не найден
        """
        try:
            params = {"telegram_user_id": telegram_user_id}

            async with api_client as client:
                response = await client._make_request(
                    method="GET", endpoint=f"api/v1/public/menu-items/{menu_item_id}/content", params=params
                )

                return response

        except APIClientError as e:
            logger.error(f"API error getting menu content: {e}")
            if "404" in str(e):
                return None
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting menu content: {e}")
            raise

    async def send_content_user(
        self,
        menu_content: Dict[str, Any],
        message_or_callback: Any,  # Message или CallbackQuery
    ) -> bool:
        """Отправляет контент пользователю.

        Args:
            menu_content: Данные контента из API
            message_or_callback: Объект сообщения или callback query

        Returns:
            True если отправка прошла успешно
        """
        from aiogram import types

        from ..utils.content_handlers import ContentHandler

        try:
            content_files = menu_content.get("content_files", [])

            if not content_files:
                # Если нет файлов контента, но есть текстовое описание
                description = menu_content.get("description", "")
                bot_message = menu_content.get("bot_message", "")

                content_text = bot_message or description or "Данные отсутствуют"

                if isinstance(message_or_callback, types.CallbackQuery):
                    await message_or_callback.message.edit_text(
                        text=content_text, parse_mode="HTML", disable_web_page_preview=True
                    )
                else:
                    await message_or_callback.answer(
                        text=content_text, parse_mode="HTML", disable_web_page_preview=True
                    )

                return True

            # Отправляем основной контент (первый файл)
            main_content = content_files[0]
            success = await ContentHandler.send_content(message_or_callback, main_content)

            # Если есть дополнительные файлы, отправляем их как сообщения
            if len(content_files) > 1 and success:
                chat_id = self._get_chat_id(message_or_callback)
                bot = self._get_bot(message_or_callback)

                for additional_content in content_files[1:]:
                    try:
                        if isinstance(message_or_callback, types.CallbackQuery):
                            additional_message = await bot.send_message(
                                chat_id=chat_id, text="📎 Дополнительный материал:"
                            )
                            await ContentHandler.send_content(additional_message, additional_content)
                        else:
                            await ContentHandler.send_content(message_or_callback, additional_content)
                    except Exception as e:
                        logger.error(f"Error sending additional content: {e}")

            return success

        except Exception as e:
            logger.error(f"Error sending content to user: {e}")
            return False

    def _get_chat_id(self, message_or_callback) -> int:
        """Получает chat_id из объекта сообщения или callback."""
        if hasattr(message_or_callback, "chat"):
            return message_or_callback.chat.id
        elif hasattr(message_or_callback, "message"):
            return message_or_callback.message.chat.id
        else:
            return message_or_callback.from_user.id

    def _get_bot(self, message_or_callback):
        """Получает бота из объекта сообщения или callback."""
        return getattr(message_or_callback, "bot", None) or message_or_callback.bot

    async def search_materials(
        self, telegram_user_id: int, query: str, limit: int = 10, page: int = 1
    ) -> List[Dict[str, Any]]:
        """Выполняет поиск материалов.

        Args:
            telegram_user_id: ID пользователя в Telegram
            query: Поисковый запрос
            limit: Количество результатов на страницу
            page: Номер страницы

        Returns:
            Список найденных материалов
        """
        try:
            params = {"telegram_user_id": telegram_user_id, "query": query, "limit": limit}

            async with api_client as client:
                response = await client._make_request(method="GET", endpoint="api/v1/public/search/", params=params)

                return response.get("items", [])

        except APIClientError as e:
            logger.error(f"API error searching materials: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error searching materials: {e}")
            raise
