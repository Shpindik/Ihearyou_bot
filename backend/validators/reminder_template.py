"""Валидатор для работы с шаблонами напоминаний."""

from __future__ import annotations

from typing import Optional

from backend.core.exceptions import ValidationError


class ReminderTemplateValidator:
    """Валидатор для работы с шаблонами напоминаний."""

    def __init__(self):
        """Инициализация валидатора Reminder Template."""
    
    def validate_template_input_data(self, data: dict):
        """Проверка корректности входящих данных для шаблона.

        Args:
            data: Словарь с входящими данными 

        Raises:
            ValidationError: Если шаблон данные не корректны
        """
        if "name" in data and data.get("name") is None:
            raise ValidationError("Имя должно быть строкой")

        if "message_template" in data and data.get("message_template") is None:
            raise ValidationError("Текст шаблона должен быть строкой")            

    def validate_template_exists(self, template: Optional[int]) -> None:
        """Проверка существования шаблона.

        Args:
            template: Объект шаблона или None

        Raises:
            ValidationError: Если шаблон не найден
        """
        if not template:
            raise ValidationError("Пункт меню не найден")
    

reminder_template_validator = ReminderTemplateValidator()
