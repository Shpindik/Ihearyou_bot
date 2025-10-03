"""Валидатор для шаблонов сообщений."""

from fastapi import HTTPException, status


class MessageTemplateValidator:
    """Валидатор для проверки данных шаблонов сообщений."""

    def __init__(self):
        """Инициализация валидатора."""

    def validate_template_exists(self, template) -> None:
        """Проверка существования шаблона.

        Args:
            template: Объект шаблона или None

        Raises:
            NotFoundError: Если шаблон не найден
        """
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Шаблон не найден")

    def validate_template_exists_for_id(self, template, template_id: int) -> None:
        """Проверка существования шаблона по ID.

        Args:
            template: Объект шаблона или None
            template_id: ID шаблона

        Raises:
            NotFoundError: Если шаблон не найден
        """
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Шаблон с ID {template_id} не найден")

    def validate_template_name(self, name: str) -> None:
        """Валидация названия шаблона.

        Args:
            name: Название шаблона

        Raises:
            ValidationError: Если название некорректно
        """
        if not name or not name.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Название шаблона не может быть пустым")

        trimmed = name.strip()
        if len(trimmed) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Название шаблона должно содержать минимум 3 символа"
            )

        if len(name) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Название шаблона не может превышать 255 символов"
            )

        # Проверка на запрещенные символы
        forbidden_chars = ["<", ">", "&", '"', "'", "\\", ";", "/"]
        if any(char in name for char in forbidden_chars):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Название содержит недопустимые символы: {forbidden_chars}",
            )

    def validate_template_content(self, content: str) -> None:
        """Валидация содержимого шаблона.

        Args:
            content: Содержимое шаблона сообщения

        Raises:
            ValidationError: Если содержимое некорректно
        """
        if not content or not content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Содержимое шаблона не может быть пустым"
            )

        trimmed = content.strip()
        if len(trimmed) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Содержимое шаблона должно содержать минимум 20 символов",
            )

        if len(content) > 4000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Содержимое шаблона не может превышать 4000 символов"
            )

        # Проверка на баланс фигурных скобок для переменных
        open_braces = content.count("{")
        close_braces = content.count("}")

        if open_braces != close_braces:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Несбалансированные фигурные скобки в шаблоне"
            )

        # Проверка на разрешенные плейсхолдеры
        valid_placeholders = [
            "{first_name}",
            "{last_name}",
            "{username}",
            "{telegram_id}",
            "{created_at}",
            "{last_activity}",
        ]

        # Находим все плейсхолдеры в тексте
        import re

        placeholders_found = re.findall(r"\{[^}]+\}", content)

        for placeholder in placeholders_found:
            if placeholder not in valid_placeholders:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Неизвестный плейсхолдер: {placeholder}. " f"Разрешенные: {', '.join(valid_placeholders)}",
                )

    def validate_search_query(self, query: str) -> None:
        """Валидация поискового запроса по названиям шаблонов.

        Args:
            query: Поисковой запрос

        Raises:
            ValidationError: Если запрос некорректен
        """
        if not query or not query.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Поисковый запрос не может быть пустым")

        trimmed = query.strip()
        if len(trimmed) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Поисковый запрос должен содержать минимум 2 символа"
            )

        if len(query) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Поисковый запрос не может превышать 100 символов"
            )

        # Проверка на потенциально опасные символы SQL injection
        sql_keywords = ["select", "insert", "update", "delete", "drop", "union", "or", "and"]
        query_lower = query.lower()

        if any(keyword in query_lower for keyword in sql_keywords):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Поисковый запрос содержит недопустимые ключевые слова"
            )

    def validate_template_activation_status(self, is_active: bool) -> None:
        """Валидация статуса активации шаблона.

        Args:
            is_active: Статус активности

        Raises:
            ValidationError: Если статус некорректен
        """
        if not isinstance(is_active, bool):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Статус активности должен быть булевым значением"
            )


message_template_validator = MessageTemplateValidator()
