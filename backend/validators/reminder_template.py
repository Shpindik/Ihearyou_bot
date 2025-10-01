"""Валидатор для работы с шаблонами напоминаний."""

from __future__ import annotations

from backend.core.exceptions import ValidationError


class ReminderTemplateValidator:
    """Валидатор для работы с шаблонами напоминаний."""

    def __init__(self):
        """Инициализация валидатора Reminder Template."""

    def validate_template_exists(self, template) -> None:
        """Проверка существования шаблона.

        Args:
            template: Объект шаблона или None

        Raises:
            ValidationError: Если шаблон не найден
        """
        if not template:
            raise ValidationError("Пункт меню не найден")


reminder_template_validator = ReminderTemplateValidator()
