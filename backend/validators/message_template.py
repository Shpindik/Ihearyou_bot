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
            HTTPException: Если шаблон не найден
        """
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Шаблон не найден")

    def validate_template_exists_for_id(self, template, template_id: int) -> None:
        """Проверка существования шаблона по ID.

        Args:
            template: Объект шаблона или None
            template_id: ID шаблона

        Raises:
            HTTPException: Если шаблон не найден
        """
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Шаблон с ID {template_id} не найден")


message_template_validator = MessageTemplateValidator()
