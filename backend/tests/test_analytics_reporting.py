"""Тесты аналитики и отчетности."""

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.admin_user import AdminUser
from backend.schemas.admin.analytics import AdminAnalyticsRequest, AdminAnalyticsResponse



@pytest.mark.unit
class TestAdminAnalyticsAPI:
    """Тесты API эндпоинтов аналитики."""

    @pytest.mark.asyncio
    async def test_get_analytics_success(self, async_client: AsyncClient, admin_token: str, db: AsyncSession):
        """Тест успешного получения аналитики."""
        # Arrange
        endpoint = "/api/v1/admin/analytics"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 200
        expected_keys = ["users", "content", "activities", "questions"]

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        # Проверяем наличие всех ожидаемых ключей
        for key in expected_keys:
            assert key in data

        # Проверяем структуру данных пользователей
        assert isinstance(data["users"], dict)
        assert "total" in data["users"]

        # Проверяем структуру контента
        assert isinstance(data["content"], dict)
        assert "total_menu_items" in data["content"]

    @pytest.mark.asyncio
    async def test_get_analytics_with_period(self, async_client: AsyncClient, admin_token: str):
        """Тест получения аналитики с различными периодами."""
        # Arrange
        endpoint = "/api/v1/admin/analytics"
        headers = {"Authorization": f"Bearer {admin_token}"}
        test_periods = ["day", "week", "month", "year"]
        expected_status_code = 200
        expected_keys = ["users", "content"]

        for period in test_periods:
            # Act
            response = await async_client.get(f"{endpoint}?period={period}", headers=headers)

            # Assert
            assert response.status_code == expected_status_code
            data = response.json()
            for key in expected_keys:
                assert key in data

    @pytest.mark.asyncio
    async def test_get_analytics_with_date_range(self, async_client: AsyncClient, admin_token: str):
        """Тест получения аналитики с диапазоном дат."""
        # Arrange
        endpoint = "/api/v1/admin/analytics"
        headers = {"Authorization": f"Bearer {admin_token}"}
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        expected_status_code = 200
        expected_key = "users"

        # Act
        response = await async_client.get(
            f"{endpoint}?start_date={start_date}&end_date={end_date}", headers=headers
        )

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_key in data

    @pytest.mark.asyncio
    async def test_get_analytics_invalid_date_format(self, async_client: AsyncClient, admin_token: str):
        """Тест получения аналитики с некорректным форматом даты."""
        # Arrange
        endpoint = "/api/v1/admin/analytics"
        headers = {"Authorization": f"Bearer {admin_token}"}
        invalid_date = "invalid-date"
        expected_status_code = 422
        expected_key = "detail"

        # Act
        response = await async_client.get(f"{endpoint}?start_date={invalid_date}", headers=headers)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_key in data

    @pytest.mark.asyncio
    async def test_get_analytics_invalid_date_range(self, async_client: AsyncClient, admin_token: str):
        """Тест получения аналитики с некорректным диапазоном дат."""
        # Arrange
        endpoint = "/api/v1/admin/analytics"
        headers = {"Authorization": f"Bearer {admin_token}"}
        start_date = "2024-01-31"
        end_date = "2024-01-01"
        expected_status_code = 422
        expected_key = "detail"

        # Act
        response = await async_client.get(f"{endpoint}?start_date={start_date}&end_date={end_date}", headers=headers)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_key in data

    @pytest.mark.asyncio
    async def test_get_analytics_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест получения аналитики без авторизации."""
        # Arrange
        endpoint = "/api/v1/admin/analytics"
        expected_status_code = 403
        expected_error_message = "Not authenticated"

        # Act
        response = await async_client_no_auth.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
        assert response.json()["error"]["message"] == expected_error_message

    @pytest.mark.asyncio
    async def test_get_analytics_invalid_token(self, async_client_no_auth: AsyncClient):
        """Тест получения аналитики с некорректным токеном."""
        # Arrange
        endpoint = "/api/v1/admin/analytics"
        headers = {"Authorization": "Bearer invalid_token"}
        expected_status_code = 401

        # Act
        response = await async_client_no_auth.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_analytics_moderator_access(self, async_client_moderator: AsyncClient):
        """Тест получения аналитики модератором (должен иметь доступ)."""
        # Arrange
        endpoint = "/api/v1/admin/analytics"
        expected_status_code = 200
        expected_keys = ["users", "content"]

        # Act
        response = await async_client_moderator.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        for key in expected_keys:
            assert key in data


@pytest.mark.unit
class TestAnalyticsService:
    """Тесты сервиса AnalyticsService."""

    @pytest.mark.asyncio
    async def test_get_analytics_success(self, analytics_service, db: AsyncSession, admin_user: AdminUser, mocker):
        """Тест успешного получения аналитики через сервис."""
        # Arrange
        request = AdminAnalyticsRequest(period="month")

        # Мокаем методы CRUD
        mock_users_stats = {"total": 100, "active_today": 10}
        mock_content_stats = {"total_menu_items": 50}
        mock_activities_stats = {"total_views": 1000}
        mock_questions_stats = {"total": 20, "pending": 5}

        mocker.patch.object(analytics_service.analytics_crud, "get_users_statistics", return_value=mock_users_stats)
        mocker.patch.object(analytics_service.analytics_crud, "get_content_statistics", return_value=mock_content_stats)
        mocker.patch.object(
            analytics_service.analytics_crud, "get_activities_statistics", return_value=mock_activities_stats
        )
        mocker.patch.object(
            analytics_service.analytics_crud, "get_questions_statistics", return_value=mock_questions_stats
        )

        # Act
        result = await analytics_service.get_analytics(db, admin_user, request)

        # Assert
        assert isinstance(result, AdminAnalyticsResponse)
        assert result.users == mock_users_stats
        assert result.content == mock_content_stats
        assert result.activities == mock_activities_stats
        assert result.questions == mock_questions_stats

    @pytest.mark.asyncio
    async def test_get_analytics_with_date_range(
        self, analytics_service, db: AsyncSession, admin_user: AdminUser, mocker
    ):
        """Тест получения аналитики с диапазоном дат."""
        # Arrange
        request = AdminAnalyticsRequest(start_date="2024-01-01", end_date="2024-01-31")

        mock_stats = {"total": 50}
        mocker.patch.object(analytics_service.analytics_crud, "get_users_statistics", return_value=mock_stats)
        mocker.patch.object(analytics_service.analytics_crud, "get_content_statistics", return_value=mock_stats)
        mocker.patch.object(analytics_service.analytics_crud, "get_activities_statistics", return_value=mock_stats)
        mocker.patch.object(analytics_service.analytics_crud, "get_questions_statistics", return_value=mock_stats)

        # Act
        result = await analytics_service.get_analytics(db, admin_user, request)

        # Assert
        assert isinstance(result, AdminAnalyticsResponse)

    @pytest.mark.asyncio
    async def test_get_analytics_invalid_admin_access(self, analytics_service, db: AsyncSession, mocker):
        """Тест получения аналитики с некорректным доступом администратора."""
        # Arrange
        request = AdminAnalyticsRequest()
        invalid_admin = mocker.MagicMock()
        invalid_admin.role = "user"  # Не админ

        # Мокаем валидатор для выбрасывания исключения
        mock_validator = mocker.patch.object(analytics_service, "validator")
        mock_validator.validate_admin_access.side_effect = Exception("Недостаточно прав")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await analytics_service.get_analytics(db, invalid_admin, request)

        assert "Недостаточно прав" in str(exc_info.value)


@pytest.mark.unit
class TestAnalyticsCRUD:
    """Тесты CRUD операций аналитики."""

    @pytest.mark.asyncio
    async def test_get_users_statistics_success(self, db: AsyncSession, analytics_crud, mocker):
        """Тест успешного получения статистики пользователей."""
        # Arrange
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

        # Мокаем результат запроса
        mock_result = mocker.MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            mocker.MagicMock(total_users=100, active_today=10, active_week=50, active_month=80)
        ]

        mock_execute = mocker.patch.object(db, "execute")
        mock_execute.return_value = mock_result

        # Act
        result = await analytics_crud.get_users_statistics(db, start_date, end_date)

        # Assert
        assert isinstance(result, dict)
        assert "total" in result

    @pytest.mark.asyncio
    async def test_get_content_statistics_success(self, db: AsyncSession, analytics_crud, mocker):
        """Тест успешного получения статистики контента."""
        # Arrange
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

        # Мокаем результат запроса
        mock_result = mocker.MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            mocker.MagicMock(total_menu_items=50, most_viewed_items=[], most_rated_items=[])
        ]

        mock_execute = mocker.patch.object(db, "execute")
        mock_execute.return_value = mock_result

        # Act
        result = await analytics_crud.get_content_statistics(db, start_date, end_date)

        # Assert
        assert isinstance(result, dict)
        assert "total_menu_items" in result

    @pytest.mark.asyncio
    async def test_get_activities_statistics_success(self, db: AsyncSession, analytics_crud, mocker):
        """Тест успешного получения статистики активностей."""
        # Arrange
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

        # Мокаем результат запроса
        mock_result = mocker.MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            mocker.MagicMock(total_views=1000, total_downloads=100, total_ratings=50, search_queries=[])
        ]

        mock_execute = mocker.patch.object(db, "execute")
        mock_execute.return_value = mock_result

        # Act
        result = await analytics_crud.get_activities_statistics(db, start_date, end_date)

        # Assert
        assert isinstance(result, dict)
        assert "total_views" in result

    @pytest.mark.asyncio
    async def test_get_questions_statistics_success(self, db: AsyncSession, analytics_crud, mocker):
        """Тест успешного получения статистики вопросов."""
        # Arrange
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

        # Мокаем результат запроса
        mock_result = mocker.MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            mocker.MagicMock(total_questions=20, pending_questions=5, answered_questions=15)
        ]

        mock_execute = mocker.patch.object(db, "execute")
        mock_execute.return_value = mock_result

        # Act
        result = await analytics_crud.get_questions_statistics(db, start_date, end_date)

        # Assert
        assert isinstance(result, dict)
        expected_keys = ["total", "pending", "answered"]
        for key in expected_keys:
            assert key in result

    def test_create_date_filters_no_dates(self, analytics_crud):
        """Тест создания фильтров по датам без дат."""
        # Arrange
        start_date = None
        end_date = None

        # Act
        filters = analytics_crud._create_date_filters(start_date, end_date)

        # Assert
        assert filters == []

    def test_create_date_filters_with_dates(self, analytics_crud):
        """Тест создания фильтров по датам с датами."""
        # Arrange
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)
        expected_filters_count = 2

        # Act
        filters = analytics_crud._create_date_filters(start_date, end_date)

        # Assert
        assert len(filters) == expected_filters_count
        assert all(f is True for f in filters)  # Placeholder values


@pytest.mark.unit
class TestAnalyticsValidator:
    """Тесты валидатора AnalyticsValidator."""

    def test_parse_and_validate_dates_with_period(self, analytics_validator, mocker):
        """Тест парсинга дат с периодом."""
        # Arrange
        request_data = {"period": "month"}

        # Act
        start_date, end_date = analytics_validator.parse_and_validate_dates(request_data)

        # Assert
        assert start_date is not None
        assert end_date is not None
        assert start_date.tzinfo == timezone.utc
        assert end_date.tzinfo == timezone.utc

    def test_parse_and_validate_dates_with_date_range(self, analytics_validator):
        """Тест парсинга дат с диапазоном."""
        # Arrange
        request_data = {"start_date": "2024-01-01", "end_date": "2024-01-31"}
        expected_start_date = datetime(2024, 1, 1).date()
        expected_end_date = datetime(2024, 1, 31).date()

        # Act
        start_date, end_date = analytics_validator.parse_and_validate_dates(request_data)

        # Assert
        assert start_date is not None
        assert end_date is not None
        assert start_date.date() == expected_start_date
        assert end_date.date() == expected_end_date

    def test_parse_and_validate_dates_invalid_date_format(self, analytics_validator):
        """Тест парсинга дат с некорректным форматом."""
        # Arrange
        from fastapi import HTTPException

        request_data = {"start_date": "invalid-date"}
        expected_status_code = 422

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            analytics_validator.parse_and_validate_dates(request_data)

        assert exc_info.value.status_code == expected_status_code

    def test_validate_admin_access_success(self, analytics_validator, mocker):
        """Тест успешной валидации доступа администратора."""
        # Arrange
        admin_user = mocker.MagicMock()
        admin_user.role = "admin"

        # Act & Assert - не должно быть исключения
        analytics_validator.validate_admin_access(admin_user)

    def test_validate_admin_access_insufficient_permissions(self, analytics_validator, mocker):
        """Тест валидации доступа с недостаточными правами."""
        # Arrange
        admin_user = mocker.MagicMock()
        admin_user.role = "user"
        expected_error_message = "Недостаточно прав"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            analytics_validator.validate_admin_access(admin_user)

        assert expected_error_message in str(exc_info.value)
