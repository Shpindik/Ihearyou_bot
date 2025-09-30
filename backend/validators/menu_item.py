"""Валидатор для работы с пунктами меню."""

from __future__ import annotations

import re
from typing import Optional

from backend.core.exceptions import ValidationError
from backend.models.enums import AccessLevel


class MenuItemValidator:
    """Валидатор бизнес-логики для пунктов меню."""

    UNSAFE_PATTERN = re.compile(r'[<>{}[\]\\|`]')
    REPEATING_PATTERN = re.compile(r'(.)\1{3,}')

    def __init__(self):
        """Инициализация валидатора Menu Item."""

    def validate_user_exists(self, user) -> None:
        """Проверка существования пользователя.

        Args:
            user: Объект пользователя или None

        Raises:
            ValidationError: Если пользователь не найден
        """
        if not user:
            raise ValidationError("Пользователь не найден. Пользователь должен быть зарегистрирован через Bot API.")

    def validate_menu_item_exists(self, menu_item) -> None:
        """Проверка существования пункта меню.

        Args:
            menu_item: Объект пункта меню или None

        Raises:
            ValidationError: Если пункт меню не найден
        """
        if not menu_item:
            raise ValidationError("Пункт меню не найден")

    def validate_menu_item_active(self, menu_item) -> None:
        """Проверка активности пункта меню.

        Args:
            menu_item: Объект пункта меню

        Raises:
            ValidationError: Если пункт меню неактивен
        """
        if not menu_item.is_active:
            raise ValidationError(f"Пункт меню '{menu_item.title}' неактивен")

    def validate_parent_menu_item(self, parent_item: Optional[object]) -> None:
        """Проверка корректности родительского пункта меню.

        Args:
            parent_item: Объект родительского пункта меню или None

        Raises:
            ValidationError: Если родительский пункт некорректен
        """
        if parent_item is None:
            raise ValidationError("Родительский пункт меню не найден")
        if not parent_item.is_active:
            raise ValidationError(f"Родительский пункт меню '{parent_item.title}' неактивен")

    def validate_access_level(self, user_access_level: AccessLevel, required_access_level: AccessLevel) -> None:
        """Проверка уровня доступа пользователя к контенту.

        Args:
            user_access_level: Уровень доступа пользователя
            required_access_level: Требуемый уровень доступа

        Raises:
            ValidationError: Если доступ запрещен
        """
        if required_access_level == AccessLevel.PREMIUM and user_access_level != AccessLevel.PREMIUM:
            raise ValidationError("Требуется доступ к премиум контенту")

    def validate_search_query(self, query: str) -> str:
        """Валидация поискового запроса.

        Args:
            query: Поисковый запрос

        Raises:
            ValidationError: Если запрос не прошел валидацию
        """
        normalized_query = ' '.join(query.split())

        if len(normalized_query) < 2 or len(normalized_query) > 100:
            raise ValidationError("Поисковый запрос должен содержать от 2 до 100 символов")

        if self.UNSAFE_PATTERN.search(normalized_query):
            raise ValidationError(
                "Поисковый запрос содержит недопустимые символы: < > { } [ ] \\ | `"
            )

        if self.REPEATING_PATTERN.search(normalized_query):
            raise ValidationError(
                "Поисковый запрос содержит слишком много повторяющихся символов"
            )

        return normalized_query


menu_item_validator = MenuItemValidator()
