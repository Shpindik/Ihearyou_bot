"""Валидатор для работы с активностью пользователей."""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status

from backend.models.enums import ActivityType


class UserActivityValidator:
    """Валидатор бизнес-логики для активности пользователей."""

    def __init__(self):
        """Инициализация валидатора User Activity."""

    def validate_user_exists(self, user) -> None:
        """Проверка существования пользователя.

        Args:
            user: Объект пользователя из БД

        Raises:
            ValidationError: Если пользователь не найден
        """
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не найден. Пользователь должен быть зарегистрирован через Bot API.",
            )

    def validate_menu_item_exists(self, menu_item) -> None:
        """Проверка существования пункта меню.

        Args:
            menu_item: Объект пункта меню из БД

        Raises:
            ValidationError: Если пункт меню не найден
        """
        if menu_item is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пункт меню не найден")

    def validate_search_query(self, search_query: Optional[str]) -> None:
        """Проверка корректности поискового запроса.

        Args:
            search_query: Поисковый запрос

        Raises:
            ValidationError: Если поисковый запрос некорректен
        """
        if search_query is None:
            return

        normalized_query = " ".join(search_query.split())

        if len(normalized_query) < 2 or len(normalized_query) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Поисковый запрос должен содержать от 2 до 100 символов"
            )

        unsafe_chars = ["<", ">", "{", "}", "[", "]", "\\", "|", "`"]
        if any(char in normalized_query for char in unsafe_chars):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поисковый запрос содержит недопустимые символы: < > { } [ ] \\ | `",
            )

        # Проверка на повторяющиеся символы (4+ подряд)
        for i in range(len(normalized_query) - 3):
            if normalized_query[i] == normalized_query[i + 1] == normalized_query[i + 2] == normalized_query[i + 3]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Поисковый запрос содержит слишком много повторяющихся символов",
                )

    def validate_rating(self, rating: Optional[int], activity_type: ActivityType) -> None:
        """Проверка корректности оценки.

        Args:
            rating: Оценка материала
            activity_type: Тип активности

        Raises:
            ValidationError: Если оценка некорректна
        """
        if activity_type == ActivityType.RATING:
            if rating is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Оценка обязательна для типа активности 'rating'"
                )
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Оценка должна быть целым числом от 1 до 5"
                )
        elif rating is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Оценка может быть указана только для типа активности 'rating'",
            )


user_activity_validator = UserActivityValidator()
