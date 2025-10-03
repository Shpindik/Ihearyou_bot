"""Утилиты для аналитики."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


def create_analytics_date_range(
    start_date: Optional[str] = None, end_date: Optional[str] = None, period: Optional[str] = None
) -> tuple[Optional[datetime], Optional[datetime]]:
    """Создать диапазон дат для аналитики.

    Args:
        start_date: Начальная дата в формате YYYY-MM-DD
        end_date: Конечная дата в формате YYYY-MM-DD
        period: Период (day, week, month, year)

    Returns:
        Кортеж (start_datetime, end_datetime) в UTC

    Raises:
        ValueError: Если формат даты некорректен или логика неверна
    """
    if not start_date and not end_date and period:
        # Используем период для автоматического определения диапазона
        end_datetime = datetime.now(timezone.utc)

        if period == "day":
            start_datetime = end_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            # Для дня берем только текущий день
        elif period == "week":
            start_datetime = end_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            # Для недели берем 7 дней назад
            from datetime import timedelta

            start_datetime = start_datetime - timedelta(days=6)  # Включая сегодня (6 дней + сегодня = 7 дней)
        elif period == "month":
            start_datetime = end_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            from datetime import timedelta

            start_datetime = start_datetime - timedelta(days=29)  # 30 дней включая сегодня
        elif period == "year":
            start_datetime = end_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            from datetime import timedelta

            start_datetime = start_datetime - timedelta(days=364)  # 365 дней включая сегодня
        else:
            raise ValueError(f"Неподдерживаемый период: {period}")

        return start_datetime, end_datetime

    # Если передан диапазон дат
    start_datetime = None
    end_datetime = None

    if start_date:
        try:
            from datetime import date

            parsed_start_date = date.fromisoformat(start_date)  # YYYY-MM-DD
            start_datetime = datetime.combine(parsed_start_date, datetime.min.time(), timezone.utc)
        except ValueError:
            raise ValueError(f"Некорректный формат начальной даты: {start_date}. Используйте YYYY-MM-DD")

    if end_date:
        try:
            from datetime import date

            parsed_end_date = date.fromisoformat(end_date)  # YYYY-MM-DD
            end_datetime = datetime.combine(parsed_end_date, datetime.max.time(), timezone.utc)
        except ValueError:
            raise ValueError(f"Некорректный формат конечной даты: {end_date}. Используйте YYYY-MM-DD")

    if start_datetime and end_datetime and start_datetime > end_datetime:
        raise ValueError("Начальная дата не может быть больше конечной даты")

    return start_datetime, end_datetime


def validate_analytics_period(period: str) -> None:
    """Валидация периода аналитики.

    Args:
        period: Период для анализа

    Raises:
        ValueError: Если период некорректен
    """
    valid_periods = {"day", "week", "month", "year"}
    if period not in valid_periods:
        raise ValueError(f"Период должен быть одним из: {', '.join(valid_periods)}")


def ensure_timezone_aware(dt: datetime) -> datetime:
    """Обеспечить, что datetime имеет информацию о временной зоне.

    Args:
        dt: Объект datetime

    Returns:
        datetime с временной зоной UTC
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
