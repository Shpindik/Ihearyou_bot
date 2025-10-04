"""Тесты аутентификации администраторов."""

import pytest
from httpx import AsyncClient


@pytest.mark.unit
class TestAdminAuthAPI:
    """Тесты API эндпоинтов аутентификации администраторов."""

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, admin_user):
        """Тест успешной аутентификации администратора."""
        # Arrange
        endpoint = "/api/v1/admin/auth/login"
        login_data = {
            "login": "testadmin@example.com",
            "password": "testpassword123"
        }
        expected_status_code = 200

        # Act
        response = await async_client.post(endpoint, json=login_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert "access_token" in data
        assert data["access_token"] is not None
        assert isinstance(data["access_token"], str)

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client: AsyncClient, admin_user):
        """Тест аутентификации с неправильным паролем."""
        # Arrange
        endpoint = "/api/v1/admin/auth/login"
        login_data = {
            "login": "testadmin@example.com",
            "password": "wrongpassword"
        }
        expected_status_code = 401

        # Act
        response = await async_client.post(endpoint, json=login_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Тест аутентификации несуществующего пользователя."""
        # Arrange
        endpoint = "/api/v1/admin/auth/login"
        login_data = {
            "login": "notadmin@example.com",
            "password": "anypassword"
        }
        expected_status_code = 401

        # Act
        response = await async_client.post(endpoint, json=login_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "login,password,expected_status",
        [
            ("", "testpassword", 422),  # Пустой login
            ("testadmin@example.com", "", 422),  # Пустой password
            ("", "", 422),  # Оба поля пустые
        ],
    )
    @pytest.mark.asyncio
    async def test_login_empty_fields(self, async_client: AsyncClient, login, password, expected_status):
        """Тест аутентификации с пустыми полями."""
        # Arrange
        endpoint = "/api/v1/admin/auth/login"
        login_data = {"login": login, "password": password}

        # Act
        response = await async_client.post(endpoint, json=login_data)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "login_data,expected_status",
        [
            ({"login": "testadmin@example.com"}, 422),  # Только login
            ({"password": "testpassword"}, 422),  # Только password
            ({}, 422),  # Пустой запрос
        ],
    )
    @pytest.mark.asyncio
    async def test_login_missing_fields(self, async_client: AsyncClient, login_data, expected_status):
        """Тест аутентификации с отсутствующими полями."""
        # Arrange
        endpoint = "/api/v1/admin/auth/login"

        # Act
        response = await async_client.post(endpoint, json=login_data)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_login_invalid_json(self, async_client: AsyncClient):
        """Тест аутентификации с некорректным JSON."""
        # Arrange
        endpoint = "/api/v1/admin/auth/login"
        invalid_content = "{not a json}"
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, content=invalid_content)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "login,password,expected_status",
        [
            ("' OR 1=1 --", "testpassword", 400),  # SQL-инъекция в login
            ("testadmin@example.com", "' OR 1=1 --", 401),  # SQL-инъекция в password
        ],
    )
    @pytest.mark.asyncio
    async def test_login_sql_injection(self, async_client: AsyncClient, login, password, expected_status):
        """Тест защиты от SQL-инъекций."""
        # Arrange
        endpoint = "/api/v1/admin/auth/login"
        login_data = {"login": login, "password": password}

        # Act
        response = await async_client.post(endpoint, json=login_data)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "field,value,expected_status",
        [
            ("login", "a" * 256, 422),  # Слишком длинный login - ошибка валидации Pydantic
            ("password", "p" * 256, 422),  # Слишком длинный password - ошибка валидации Pydantic
        ],
    )
    @pytest.mark.asyncio
    async def test_login_field_length_limits(self, async_client: AsyncClient, field, value, expected_status):
        """Тест ограничений длины полей."""
        # Arrange
        endpoint = "/api/v1/admin/auth/login"
        login_data = {
            "login": "testadmin@example.com",
            "password": "testpassword123"
        }
        login_data[field] = value

        # Act
        response = await async_client.post(endpoint, json=login_data)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_login_case_sensitivity(self, async_client: AsyncClient, admin_user):
        """Тест чувствительности к регистру при аутентификации."""
        # Arrange
        endpoint = "/api/v1/admin/auth/login"
        login_data = {
            "login": "Testadmin@example.com",  # Изменен регистр
            "password": "testpassword123"
        }
        expected_status_code = 401

        # Act
        response = await async_client.post(endpoint, json=login_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert "detail" in data
