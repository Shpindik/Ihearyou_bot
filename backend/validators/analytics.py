"""Валидатор для работы с аналитикой."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from backend.core.exceptions import ValidationError


class AnalyticsValidator:
    """Валидатор для аналитических запросов."""

    def __init__(self):
        """Инициализация валидатора Analytics."""

    def validate_period(self, period: str) -> None:
        """Валидация периода аналитики.

        Args:
            period: Период для анализа

        Raises:
            ValidationError: Если период некорректен

        """
        if period not in ["day", "week", "month", "year"]:
            raise ValidationError("Период должен быть одним из: day, week, month, year")

    def validate_date_range(
        self,
        start_date: Optional[str],
        end_date: Optional[str],
        period: Optional[str] = None,
    ) -> Optional[tuple]:
        """Валидация диапазона дат.

        Args:
            start_date: Начальная дата (ISO 8601)
            end_date: Конечная дата (ISO 8601)
            period: Период (если указан)

        Returns:
            Кортеж с преобразованными датами или None

        Raises:
            ValidationError: Если диапазон дат некорректен

        """
        if period is None and start_date is None and end_date is None:
            return None

        parsed_start = None
        parsed_end = None

        if start_date:
            try:
                parsed_start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            except ValueError:
                raise ValidationError("Начальная дата должна быть в формате ISO 8601 (YYYY-MM-DDTHH:MM:SS)")

        if end_date:
            try:
                parsed_end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            except ValueError:
                raise ValidationError("Конечная дата должна быть в формате ISO 8601 (YYYY-MM-DDTHH:MM:SS)")

        if parsed_start and parsed_end and parsed_start > parsed_end:
            raise ValidationError("Начальная дата не может быть больше конечной даты")

        return parsed_start, parsed_end

    def validate_admin_access(self, admin_user) -> None:
        """Проверка доступа администратора к аналитике.

        Args:
            admin_user: Объект администратора

        Raises:
            ValidationError: Если доступ запрещен

        """
        if not admin_user:
            raise ValidationError("Требуется аутентификация администратора")

        if not admin_user.is_active:
            raise ValidationError("Учетная запись администратора неактивна")

        if admin_user.role.value not in ["admin", "moderator"]:
            raise ValidationError("Недостаточно прав для доступа к аналитике")


analytics_validator = AnalyticsValidator()
