"""Валидатор для работы с пунктами меню."""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status

from backend.models.enums import AccessLevel


class MenuItemValidator:
    """Валидатор бизнес-логики для пунктов меню."""

    def __init__(self):
        """Инициализация валидатора Menu Item."""

    def validate_user_exists(self, user) -> None:
        """Проверка существования пользователя.

        Args:
            user: Объект пользователя или None

        Raises:
            HTTPException: Если пользователь не найден
        """
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден. Пользователь должен быть зарегистрирован через Bot API.",
            )

    def validate_menu_item_exists(self, menu_item) -> None:
        """Проверка существования пункта меню.

        Args:
            menu_item: Объект пункта меню или None

        Raises:
            HTTPException: Если пункт меню не найден
        """
        if not menu_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пункт меню не найден")

    def validate_menu_item_active(self, menu_item) -> None:
        """Проверка активности пункта меню.

        Args:
            menu_item: Объект пункта меню

        Raises:
            HTTPException: Если пункт меню неактивен
        """
        if not menu_item.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Пункт меню '{menu_item.title}' неактивен"
            )

    def validate_parent_menu_item(self, parent_item: Optional[object]) -> None:
        """Проверка корректности родительского пункта меню.

        Args:
            parent_item: Объект родительского пункта меню или None

        Raises:
            HTTPException: Если родительский пункт некорректен
        """
        if parent_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Родительский пункт меню не найден")
        if not parent_item.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Родительский пункт меню '{parent_item.title}' неактивен"
            )

    def validate_access_level(self, user_access_level: AccessLevel, required_access_level: AccessLevel) -> None:
        """Проверка уровня доступа пользователя к контенту.

        Args:
            user_access_level: Уровень доступа пользователя
            required_access_level: Требуемый уровень доступа

        Raises:
            HTTPException: Если доступ запрещен
        """
        if required_access_level == AccessLevel.PREMIUM and user_access_level != AccessLevel.PREMIUM:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Требуется доступ к премиум контенту")

    def validate_menu_item_not_self_parent(self, menu_id: int) -> None:
        """Проверка, что пункт меню не является родителем самому себе.

        Args:
            menu_id: ID пункта меню

        Raises:
            HTTPException: Если пункт меню является родителем самому себе
        """
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Пункт меню не может быть родителем самому себе"
        )

    def validate_menu_item_no_children(self, children: list) -> None:
        """Проверка, что у пункта меню нет дочерних элементов.

        Args:
            children: Список дочерних элементов

        Raises:
            HTTPException: Если есть дочерние элементы
        """
        if children:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить пункт меню, у которого есть дочерние элементы",
            )

    def validate_search_query(self, query: str) -> str:
        """Валидация поискового запроса.

        Args:
            query: Поисковый запрос (уже прошедший pydantic валидацию длины)

        Raises:
            HTTPException: Если запрос не прошел валидацию
        """
        normalized_query = " ".join(query.split())

        unsafe_chars = ["<", ">", "{", "}", "[", "]", "\\", "|", "`"]
        if any(char in normalized_query for char in unsafe_chars):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поисковый запрос содержит недопустимые символы: < > { } [ ] \\ | `",
            )

        for i in range(len(normalized_query) - 3):
            if normalized_query[i] == normalized_query[i + 1] == normalized_query[i + 2] == normalized_query[i + 3]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Поисковый запрос содержит слишком много повторяющихся символов",
                )

        return normalized_query


menu_item_validator = MenuItemValidator()
