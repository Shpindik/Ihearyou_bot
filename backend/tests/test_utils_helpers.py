"""Тесты утилит и вспомогательных функций."""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from backend.utils.analytics import create_analytics_date_range, ensure_timezone_aware, validate_analytics_period


@pytest.mark.unit
class TestAnalyticsUtils:
    """Тесты утилит для аналитики."""

    def test_create_analytics_date_range_with_period_day(self):
        """Тест создания диапазона дат для периода 'day'."""
        # Arrange
        period = "day"
        tolerance_seconds = 60

        # Act
        start_date, end_date = create_analytics_date_range(period=period)

        # Assert
        assert start_date is not None
        assert end_date is not None
        assert start_date.tzinfo == timezone.utc
        assert end_date.tzinfo == timezone.utc

        # Для периода day start_date должен быть началом текущего дня
        now = datetime.now(timezone.utc)
        expected_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        assert abs((start_date - expected_start).total_seconds()) < tolerance_seconds

    def test_create_analytics_date_range_with_period_week(self):
        """Тест создания диапазона дат для периода 'week'."""
        # Arrange
        period = "week"
        tolerance_seconds = 60
        days_back = 6

        # Act
        start_date, end_date = create_analytics_date_range(period=period)

        # Assert
        assert start_date is not None
        assert end_date is not None
        assert start_date.tzinfo == timezone.utc
        assert end_date.tzinfo == timezone.utc

        # Для периода week start_date должен быть 6 дней назад от начала дня
        now = datetime.now(timezone.utc)
        expected_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        expected_start = expected_start - timedelta(days=days_back)
        assert abs((start_date - expected_start).total_seconds()) < tolerance_seconds

    def test_create_analytics_date_range_with_period_month(self):
        """Тест создания диапазона дат для периода 'month'."""
        # Arrange
        period = "month"
        tolerance_seconds = 86400  # Разница не более дня
        days_back = 29

        # Act
        start_date, end_date = create_analytics_date_range(period=period)

        # Assert
        assert start_date is not None
        assert end_date is not None
        assert start_date.tzinfo == timezone.utc
        assert end_date.tzinfo == timezone.utc

        # Для периода month start_date должен быть 29 дней назад от начала дня
        now = datetime.now(timezone.utc)
        expected_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        expected_start = expected_start - timedelta(days=days_back)
        assert abs((start_date - expected_start).total_seconds()) < tolerance_seconds

    def test_create_analytics_date_range_with_period_year(self):
        """Тест создания диапазона дат для периода 'year'."""
        # Arrange
        period = "year"
        tolerance_seconds = 86400  # Разница не более дня
        days_back = 364

        # Act
        start_date, end_date = create_analytics_date_range(period=period)

        # Assert
        assert start_date is not None
        assert end_date is not None
        assert start_date.tzinfo == timezone.utc
        assert end_date.tzinfo == timezone.utc

        # Для периода year start_date должен быть 364 дня назад от начала дня
        now = datetime.now(timezone.utc)
        expected_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        expected_start = expected_start - timedelta(days=days_back)
        assert abs((start_date - expected_start).total_seconds()) < tolerance_seconds

    def test_create_analytics_date_range_invalid_period(self):
        """Тест создания диапазона дат с некорректным периодом."""
        # Arrange
        invalid_period = "invalid"
        expected_error_message = "Неподдерживаемый период"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            create_analytics_date_range(period=invalid_period)

        assert expected_error_message in str(exc_info.value)

    def test_create_analytics_date_range_with_dates(self):
        """Тест создания диапазона дат с явными датами."""
        # Arrange
        start_date_str = "2024-01-01"
        end_date_str = "2024-01-31"
        expected_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        expected_end = datetime(2024, 1, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)

        # Act
        start_date, end_date = create_analytics_date_range(start_date=start_date_str, end_date=end_date_str)

        # Assert
        assert start_date is not None
        assert end_date is not None
        assert start_date.tzinfo == timezone.utc
        assert end_date.tzinfo == timezone.utc
        assert start_date == expected_start
        assert end_date == expected_end

    def test_create_analytics_date_range_invalid_date_format(self):
        """Тест создания диапазона дат с некорректным форматом даты."""
        # Arrange
        invalid_date = "invalid-date"
        expected_error_message = "Некорректный формат начальной даты"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            create_analytics_date_range(start_date=invalid_date)

        assert expected_error_message in str(exc_info.value)

    def test_create_analytics_date_range_end_before_start(self):
        """Тест создания диапазона дат, где конечная дата раньше начальной."""
        # Arrange
        start_date_str = "2024-01-31"
        end_date_str = "2024-01-01"
        expected_error_message = "Начальная дата не может быть больше конечной даты"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            create_analytics_date_range(start_date=start_date_str, end_date=end_date_str)

        assert expected_error_message in str(exc_info.value)

    def test_validate_analytics_period_valid(self):
        """Тест валидации корректных периодов аналитики."""
        # Arrange
        valid_periods = ["day", "week", "month", "year"]

        # Act & Assert - эти периоды должны проходить без исключений
        for period in valid_periods:
            validate_analytics_period(period)

    def test_validate_analytics_period_invalid(self):
        """Тест валидации некорректных периодов аналитики."""
        # Arrange
        invalid_period = "invalid"
        expected_error_message = "Период должен быть одним из"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            validate_analytics_period(invalid_period)

        assert expected_error_message in str(exc_info.value)

    def test_ensure_timezone_aware_naive_datetime(self):
        """Тест добавления timezone к naive datetime."""
        # Arrange
        naive_dt = datetime(2024, 1, 1, 12, 0, 0)
        expected_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Act
        result = ensure_timezone_aware(naive_dt)

        # Assert
        assert result.tzinfo == timezone.utc
        assert result == expected_dt

    def test_ensure_timezone_aware_aware_datetime(self):
        """Тест обработки уже aware datetime."""
        # Arrange
        aware_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Act
        result = ensure_timezone_aware(aware_dt)

        # Assert
        assert result == aware_dt
        assert result.tzinfo == timezone.utc


@pytest.mark.unit
@pytest.mark.asyncio
class TestEmailService:
    """Тесты сервиса отправки email."""

    async def test_send_password_reset_email_success(self, email_service):
        """Тест успешной отправки email для восстановления пароля."""
        # Arrange
        email = "test@example.com"
        reset_token = "test-token"
        admin_name = "Test Admin"
        expected_subject = "Восстановление пароля - Админ-панель"
        expected_url_base = "http://test.com"

        # Act
        await email_service.send_password_reset_email(email, reset_token, admin_name)

        # Assert
        email_service.fastmail.send_message.assert_called_once()
        call_args = email_service.fastmail.send_message.call_args[0][0]

        assert call_args.subject == expected_subject
        assert email in call_args.recipients
        assert "html" in call_args.body
        assert admin_name in call_args.body
        assert reset_token in call_args.body
        assert expected_url_base in call_args.body

    async def test_send_password_reset_email_default_name(self, email_service):
        """Тест отправки email с именем по умолчанию."""
        # Arrange
        email = "test@example.com"
        reset_token = "test-token"
        expected_default_name = "Администратор"

        # Act
        await email_service.send_password_reset_email(email, reset_token)

        # Assert
        email_service.fastmail.send_message.assert_called_once()
        call_args = email_service.fastmail.send_message.call_args[0][0]

        assert expected_default_name in call_args.body

    async def test_send_password_reset_email_html_content(self, email_service):
        """Тест содержимого HTML письма."""
        # Arrange
        email = "test@example.com"
        reset_token = "test-token"
        admin_name = "Test Admin"
        expected_html_elements = [
            "<!DOCTYPE html>",
            "<h2>Восстановление пароля</h2>",
            f"Здравствуйте, {admin_name}!",
            "Сменить пароль"
        ]
        expected_url = f"http://test.com/admin/reset-password?token={reset_token}"
        unexpected_content = "Вернитесь к нам 🥰"

        # Act
        await email_service.send_password_reset_email(email, reset_token, admin_name)

        # Assert
        call_args = email_service.fastmail.send_message.call_args[0][0]
        html_body = call_args.body

        # Проверяем ключевые элементы HTML
        for element in expected_html_elements:
            assert element in html_body

        assert unexpected_content not in html_body
        assert reset_token in html_body
        assert expected_url in html_body

    async def test_send_password_reset_email_fastmail_error(self, email_service):
        """Тест обработки ошибок FastMail."""
        # Arrange
        email = "test@example.com"
        reset_token = "token"
        smtp_error = "SMTP Error"
        expected_status_code = 500
        expected_error_message = "Ошибка отправки письма"

        email_service.fastmail.send_message.side_effect = Exception(smtp_error)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await email_service.send_password_reset_email(email, reset_token)

        assert exc_info.value.status_code == expected_status_code
        assert expected_error_message in str(exc_info.value.detail)
        assert smtp_error in str(exc_info.value.detail)
