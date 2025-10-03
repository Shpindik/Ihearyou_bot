"""Сервис для работы с вопросами пользователей."""

import logging
from typing import Any, Dict, Optional

from ..utils.api_client import APIClientError, api_client


logger = logging.getLogger(__name__)


class QuestionService:
    """Сервис для работы с вопросами пользователей."""

    async def submit_question(self, telegram_user_id: int, question_text: str) -> Optional[Dict[str, Any]]:
        """Отправляет вопрос пользователя в API.

        Args:
            telegram_user_id: ID пользователя в Telegram
            question_text: Текст вопроса

        Returns:
            Данные созданного вопроса или None при ошибке
        """
        try:
            question_data = {"telegram_user_id": telegram_user_id, "question_text": question_text}

            async with api_client as client:
                response = await client._make_request(
                    method="POST", endpoint="api/v1/public/user-questions/", data=question_data
                )

                logger.debug(f"Question submitted for user {telegram_user_id}: {response}")
                return response

        except APIClientError as e:
            logger.error(f"API error submitting question: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error submitting question: {e}")
            return None
