"""Валидатор для работы с аналитикой."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status

from backend.utils.analytics import create_analytics_date_range, ensure_timezone_aware


class AnalyticsValidator:
    """Валидатор для аналитических запросов - только бизнес-логика."""

    def __init__(self):
        """Инициализация валидатора Analytics."""

    def parse_and_validate_dates(self, request_data: dict) -> tuple[Optional[datetime], Optional[datetime]]:
        """Финальная обработка дат после валидации в схемах.

        Args:
            request_data: Данные запроса с уже валидированными полями

        Returns:
            Кортеж с обработанными датами в UTC

        Raises:
            HTTPException: Если что-то пошло не так с обработкой дат
        """
        try:
            period = request_data.get("period")
            start_date = request_data.get("start_date")
            end_date = request_data.get("end_date")

            # Используем утилиту для создания диапазона дат
            parsed_start, parsed_end = create_analytics_date_range(start_date, end_date, period)

            # Обеспечиваем timezone awareness
            if parsed_start:
                parsed_start = ensure_timezone_aware(parsed_start)
            if parsed_end:
                parsed_end = ensure_timezone_aware(parsed_end)

            return parsed_start, parsed_end

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def validate_admin_access(self, admin_user) -> None:
        """Проверка доступа администратора к аналитике.

        Args:
            admin_user: Объект администратора

        Raises:
            HTTPException: Если доступ запрещен

        """
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется аутентификация администратора"
            )

        if not admin_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Учетная запись администратора неактивна"
            )

        role_value = admin_user.role.value if hasattr(admin_user.role, "value") else str(admin_user.role)
        if role_value not in ["admin", "moderator"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для доступа к аналитике"
            )


analytics_validator = AnalyticsValidator()
