"""Валидатор для работы с активностью пользователей."""

from __future__ import annotations

from typing import Optional

from backend.core.exceptions import ValidationError
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
            raise ValidationError("Пользователь не найден. Пользователь должен быть зарегистрирован через Bot API.")

    def validate_menu_item_exists(self, menu_item) -> None:
        """Проверка существования пункта меню.

        Args:
            menu_item: Объект пункта меню из БД

        Raises:
            ValidationError: Если пункт меню не найден
        """
        if menu_item is None:
            raise ValidationError("Пункт меню не найден")

    def validate_search_query(self, search_query: Optional[str]) -> None:
        """Проверка корректности поискового запроса.

        Args:
            search_query: Поисковый запрос

        Raises:
            ValidationError: Если поисковый запрос некорректен
        """
        if search_query is None:
            return

        if len(search_query) < 2:
            raise ValidationError("Поисковый запрос должен содержать минимум 2 символа")
        if len(search_query) > 100:
            raise ValidationError("Поисковый запрос не может превышать 100 символов")

        if len(search_query) > 5:
            if len(set(search_query)) < 3:
                raise ValidationError("Поисковый запрос содержит слишком много повторяющихся символов")

        forbidden_chars = ["<", ">", "&", '"', "'", "\\", "/", ";"]
        if any(char in search_query for char in forbidden_chars):
            raise ValidationError("Поисковый запрос содержит недопустимые символы")

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
                raise ValidationError("Оценка обязательна для типа активности 'rating'")
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                raise ValidationError("Оценка должна быть целым числом от 1 до 5")
        elif rating is not None:
            raise ValidationError("Оценка может быть указана только для типа активности 'rating'")


user_activity_validator = UserActivityValidator()
