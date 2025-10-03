"""Сервис для работы с активностью пользователей."""

import logging
from typing import Optional

from ..utils.api_client import APIClientError, api_client


logger = logging.getLogger(__name__)


class UserActivityService:
    """Сервис для логирования активности пользователей."""

    async def log_activity(
        self,
        telegram_user_id: int,
        activity_type: str,
        menu_item_id: Optional[int] = None,
        search_query: Optional[str] = None,
        rating: Optional[int] = None,
    ) -> bool:
        """Логирует активность пользователя.

        Args:
            telegram_user_id: ID пользователя в Telegram
            activity_type: Тип активности
            menu_item_id: ID пункта меню (если применимо)
            search_query: Поисковый запрос (если применимо)
            rating: Оценка материала (если применимо)

        Returns:
            True если логирование прошло успешно
        """
        try:
            activity_data = {
                "telegram_user_id": telegram_user_id,
                "activity_type": activity_type,
                "menu_item_id": menu_item_id,
                "search_query": search_query,
                "rating": rating,
            }

            # Убираем None значения
            activity_data = {k: v for k, v in activity_data.items() if v is not None}

            async with api_client as client:
                response = await client._make_request(
                    method="POST", endpoint="api/v1/public/user-activities/", data=activity_data
                )

                logger.debug(f"Logged activity for user {telegram_user_id}: {response}")
                return True

        except APIClientError as e:
            logger.error(f"API error logging activity: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error logging activity: {e}")
            return False

    async def log_menu_navigation(self, telegram_user_id: int, menu_item_id: int) -> bool:
        """Логирует навигацию по меню."""
        return await self.log_activity(
            telegram_user_id=telegram_user_id, activity_type="navigation", menu_item_id=menu_item_id
        )

    async def log_content_view(self, telegram_user_id: int, menu_item_id: int, content_title: str) -> bool:
        """Логирует просмотр контента."""
        return await self.log_activity(
            telegram_user_id=telegram_user_id, activity_type="content_view", menu_item_id=menu_item_id
        )

    async def log_search(self, telegram_user_id: int, search_query: str) -> bool:
        """Логирует поисковый запрос."""
        return await self.log_activity(
            telegram_user_id=telegram_user_id, activity_type="search", search_query=search_query
        )

    async def log_rating(self, telegram_user_id: int, menu_item_id: int, rating: int) -> bool:
        """Логирует оценку материала."""
        return await self.log_activity(
            telegram_user_id=telegram_user_id, activity_type="rating", menu_item_id=menu_item_id, rating=rating
        )

    async def log_question_ask(self, telegram_user_id: int) -> bool:
        """Логирует факт задавания вопроса."""
        return await self.log_activity(telegram_user_id=telegram_user_id, activity_type="question_ask")
