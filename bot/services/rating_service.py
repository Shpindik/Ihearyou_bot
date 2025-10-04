"""Сервис для работы с оценками материалов."""

import logging
from typing import Any, Dict, Optional

from ..utils.api_client import APIClientError, api_client


logger = logging.getLogger(__name__)


class RatingService:
    """Сервис для работы с оценками материалов."""

    async def submit_rating(self, telegram_user_id: int, menu_item_id: int, rating: int) -> bool:
        """Отправляет оценку пользователя в API.

        Args:
            telegram_user_id: ID пользователя в Telegram
            menu_item_id: ID пункта меню
            rating: Оценка от 1 до 5

        Returns:
            True если оценка успешно сохранена
        """
        try:
            rating_data = {"telegram_user_id": telegram_user_id, "menu_item_id": menu_item_id, "rating": rating}

            async with api_client as client:
                response = await client._make_request(
                    method="POST", endpoint="api/v1/public/ratings/", data=rating_data
                )

                logger.debug(f"Rating submitted for user {telegram_user_id}: {response}")
                return True

        except APIClientError as e:
            logger.error(f"API error submitting rating: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error submitting rating: {e}")
            return False

    async def get_menu_item_info(self, menu_item_id: int, telegram_user_id: int) -> Optional[Dict[str, Any]]:
        """Получает информацию о пункте меню.

        Args:
            menu_item_id: ID пункта меню
            telegram_user_id: ID Telegram пользователя

        Returns:
            Информация о пункте меню или None
        """
        try:
            async with api_client as client:
                response = await client._make_request(
                    method="GET",
                    endpoint=f"api/v1/public/menu-items/{menu_item_id}/content",
                    params={"telegram_user_id": telegram_user_id},
                )

                # Возвращаем только нужные поля
                return {
                    "id": response.get("id"),
                    "title": response.get("title"),
                    "item_type": response.get("item_type"),
                }

        except APIClientError as e:
            logger.error(f"API error Getting menu item info: {e}")
            if "404" in str(e):
                return None
            return None
        except Exception as e:
            logger.error(f"Unexpected error Getting menu item info: {e}")
            return None
