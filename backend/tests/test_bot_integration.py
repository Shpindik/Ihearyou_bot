"""Тесты интеграции с Telegram ботом."""

import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.telegram_user import TelegramUser
from backend.schemas.bot.message_template import BotMessageTemplateResponse
from backend.schemas.bot.telegram_user import (
    BotInactiveUserResponse,
    BotReminderStatusResponse,
    TelegramUserRequest,
    TelegramUserResponse,
)
from backend.services.message_template import message_template_service
from backend.services.telegram_user import telegram_user_service


@pytest.mark.unit
class TestBotTelegramUserAPI:
    """Тесты Bot API для пользователей Telegram."""

    @pytest.mark.asyncio
    async def test_register_telegram_user_success_new_user(self, async_client: AsyncClient):
        """Тест успешной регистрации нового пользователя Telegram."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/register"
        user_data = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "from": {"id": 123456789, "first_name": "Test", "last_name": "User", "username": "testuser"},
                "chat": {"id": 123456789},
            },
        }
        expected_status_code = 200
        expected_user_data = {
            "telegram_id": 123456789,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "subscription_type": "free"
        }

        # Act
        response = await async_client.post(endpoint, json=user_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        assert data["user"]["telegram_id"] == expected_user_data["telegram_id"]
        assert data["user"]["first_name"] == expected_user_data["first_name"]
        assert data["user"]["last_name"] == expected_user_data["last_name"]
        assert data["user"]["username"] == expected_user_data["username"]
        assert data["user"]["subscription_type"] == expected_user_data["subscription_type"]
        assert "id" in data["user"]
        assert "created_at" in data["user"]
        assert data["user_created"] is True

    @pytest.mark.asyncio
    async def test_register_telegram_user_success_existing_user(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест успешного обновления существующего пользователя Telegram."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/register"
        existing_user = telegram_users_fixture[0]
        updated_data = {
            "update_id": 123457,
            "message": {
                "message_id": 2,
                "from": {
                    "id": existing_user.telegram_id,
                    "first_name": "Updated",
                    "last_name": "Name",
                    "username": "updateduser",
                },
                "chat": {"id": existing_user.telegram_id},
            },
        }
        expected_status_code = 200

        # Act
        response = await async_client.post(endpoint, json=updated_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        assert data["user"]["telegram_id"] == existing_user.telegram_id
        assert data["user"]["first_name"] == "Updated"
        assert data["user"]["last_name"] == "Name"
        assert data["user"]["username"] == "updateduser"
        assert data["user_updated"] is True

    @pytest.mark.asyncio
    async def test_register_telegram_user_invalid_data(self, async_client: AsyncClient):
        """Тест регистрации пользователя с некорректными данными."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/register"
        invalid_data = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "from": {"id": -1, "first_name": "Test"},  # Отрицательный telegram_id
                "chat": {"id": -1},
            },
        }
        expected_status_code = 400

        # Act
        response = await async_client.post(endpoint, json=invalid_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_register_telegram_user_missing_user_data(self, async_client: AsyncClient):
        """Тест регистрации с отсутствующими данными пользователя."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/register"
        invalid_data = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "from": {},  # Пустой объект from
                "chat": {"id": 123456789},
            },
        }
        expected_status_code = 400
        expected_error_message = "Отсутствуют данные пользователя в запросе"

        # Act
        response = await async_client.post(endpoint, json=invalid_data)

        # Assert
        assert response.status_code == expected_status_code
        assert expected_error_message in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_telegram_user_malformed_json(self, async_client: AsyncClient):
        """Тест регистрации с некорректным JSON."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/register"
        headers = {"Content-Type": "application/json"}
        invalid_data = "invalid json"
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, data=invalid_data, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_inactive_users_for_reminders_success(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест успешного получения неактивных пользователей для напоминаний."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/inactive-users"
        params = {"inactive_days": 1, "days_since_last_reminder": 1}
        expected_status_code = 200

        # Act
        response = await async_client.get(endpoint, params=params)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        assert isinstance(data, list)

        # Проверяем структуру ответа
        if data:
            user = data[0]
            required_fields = ["telegram_id", "first_name", "last_name", "username", "last_activity", "reminder_sent_at"]
            for field in required_fields:
                assert field in user

    @pytest.mark.asyncio
    async def test_get_inactive_users_for_reminders_with_params(self, async_client: AsyncClient):
        """Тест получения неактивных пользователей с различными параметрами."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/inactive-users"
        test_cases = [
            {"inactive_days": 10, "days_since_last_reminder": 10},
            {"inactive_days": 30, "days_since_last_reminder": 7},
            {"inactive_days": 1, "days_since_last_reminder": 30},
        ]
        expected_status_code = 200

        for params in test_cases:
            # Act
            response = await async_client.get(endpoint, params=params)

            # Assert
            assert response.status_code == expected_status_code
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_inactive_users_for_reminders_invalid_params(self, async_client: AsyncClient):
        """Тест получения неактивных пользователей с некорректными параметрами."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/inactive-users"
        invalid_params = {"inactive_days": 0, "days_since_last_reminder": -1}
        expected_status_code = 422

        # Act
        response = await async_client.get(endpoint, params=invalid_params)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_inactive_users_empty_result(self, async_client: AsyncClient):
        """Тест получения пустого списка неактивных пользователей."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/inactive-users"
        expected_status_code = 200
        expected_empty_result = []

        # Act
        response = await async_client.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
        assert response.json() == expected_empty_result

    @pytest.mark.asyncio
    async def test_update_reminder_status_success(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест успешного обновления статуса отправки напоминания."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/update-reminder-status"
        user = telegram_users_fixture[0]
        params = {"telegram_user_id": user.telegram_id}
        expected_status_code = 200

        # Act
        response = await async_client.post(endpoint, params=params)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        assert data["success"] == "true"
        assert "reminder_sent_at" in data

    @pytest.mark.asyncio
    async def test_update_reminder_status_user_not_found(self, async_client: AsyncClient):
        """Тест обновления статуса напоминания для несуществующего пользователя."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/update-reminder-status"
        non_existent_id = 999999
        params = {"telegram_user_id": non_existent_id}
        expected_status_code = 404

        # Act
        response = await async_client.post(endpoint, params=params)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_update_reminder_status_invalid_telegram_id(self, async_client: AsyncClient):
        """Тест обновления статуса напоминания с некорректным telegram_id."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/update-reminder-status"
        invalid_params = {"telegram_user_id": -1}
        expected_status_code = 404

        # Act
        response = await async_client.post(endpoint, params=invalid_params)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_update_reminder_status_invalid_param_type(self, async_client: AsyncClient):
        """Тест обновления статуса напоминания с некорректным типом параметра."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/update-reminder-status"
        invalid_params = {"telegram_user_id": "not_a_number"}
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, params=invalid_params)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_update_reminder_status_missing_param(self, async_client: AsyncClient):
        """Тест обновления статуса напоминания без обязательного параметра."""
        # Arrange
        endpoint = "/api/v1/bot/telegram-user/update-reminder-status"
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint)

        # Assert
        assert response.status_code == expected_status_code


@pytest.mark.unit
class TestBotMessageTemplateAPI:
    """Тесты Bot API для шаблонов сообщений."""

    @pytest.mark.asyncio
    async def test_get_active_message_template_success(self, async_client: AsyncClient):
        """Тест успешного получения активного шаблона сообщения."""
        # Arrange
        endpoint = "/api/v1/bot/message-template/active-template"
        expected_status_code = 200
        required_fields = ["id", "name", "message_template", "created_at"]

        # Act
        response = await async_client.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        for field in required_fields:
            assert field in data

        # Проверяем, что шаблон содержит персонализацию
        assert "{first_name}" in data["message_template"]

    @pytest.mark.asyncio
    async def test_get_active_message_template_always_returns_template(self, async_client: AsyncClient):
        """Тест получения активного шаблона - сервис всегда возвращает шаблон."""
        # Arrange
        endpoint = "/api/v1/bot/message-template/active-template"
        expected_status_code = 200
        required_fields = ["id", "name", "message_template", "created_at"]

        # Act
        response = await async_client.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        for field in required_fields:
            assert field in data


@pytest.mark.unit
class TestTelegramUserService:
    """Тесты сервиса TelegramUserService для Bot API."""

    @pytest.mark.asyncio
    async def test_register_user_success_new_user(self, db: AsyncSession):
        """Тест успешной регистрации нового пользователя через сервис."""
        # Arrange
        request = TelegramUserRequest(
            update_id=123456,
            message={
                "message_id": 1,
                "from": {"id": 987654321, "first_name": "New", "last_name": "User", "username": "newuser"},
                "chat": {"id": 987654321},
            },
        )
        expected_telegram_id = 987654321
        expected_subscription_type = "free"

        # Act
        result = await telegram_user_service.register_user(request, db)

        # Assert
        assert isinstance(result, TelegramUserResponse)
        assert result.user["telegram_id"] == expected_telegram_id
        assert result.user["first_name"] == request.message["from"]["first_name"]
        assert result.user["last_name"] == request.message["from"]["last_name"]
        assert result.user["username"] == request.message["from"]["username"]
        assert result.user["subscription_type"] == expected_subscription_type

    @pytest.mark.asyncio
    async def test_register_user_success_existing_user(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест успешного обновления существующего пользователя через сервис."""
        # Arrange
        existing_user = telegram_users_fixture[0]
        request = TelegramUserRequest(
            update_id=123457,
            message={
                "message_id": 2,
                "from": {
                    "id": existing_user.telegram_id,
                    "first_name": "Updated",
                    "last_name": "Name",
                    "username": "updateduser",
                },
                "chat": {"id": existing_user.telegram_id},
            },
        )

        # Act
        result = await telegram_user_service.register_user(request, db)

        # Assert
        assert isinstance(result, TelegramUserResponse)
        assert result.user["telegram_id"] == existing_user.telegram_id
        assert result.user["first_name"] == request.message["from"]["first_name"]

    @pytest.mark.asyncio
    async def test_get_inactive_users_success(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест успешного получения неактивных пользователей."""
        # Arrange
        inactive_days = 1
        days_since_last_reminder = 1

        # Act
        result = await telegram_user_service.get_inactive_users(
            db=db, 
            inactive_days=inactive_days, 
            days_since_last_reminder=days_since_last_reminder
        )

        # Assert
        assert isinstance(result, list)
        for user in result:
            assert isinstance(user, BotInactiveUserResponse)
            assert hasattr(user, "telegram_id")
            assert hasattr(user, "first_name")

    @pytest.mark.asyncio
    async def test_update_reminder_status_success(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест успешного обновления статуса напоминания через сервис."""
        # Arrange
        user = telegram_users_fixture[0]
        expected_success_value = "true"

        # Act
        result = await telegram_user_service.update_reminder_status(db=db, telegram_user_id=user.telegram_id)

        # Assert
        assert isinstance(result, BotReminderStatusResponse)
        assert result.success == expected_success_value
        assert result.reminder_sent_at is not None

    @pytest.mark.asyncio
    async def test_update_reminder_status_user_not_found(self, db: AsyncSession):
        """Тест обновления статуса напоминания для несуществующего пользователя через сервис."""
        # Arrange
        non_existent_id = 999999
        expected_status_code = 404
        expected_error_message = "Пользователь не найден"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await telegram_user_service.update_reminder_status(db=db, telegram_user_id=non_existent_id)

        assert exc_info.value.status_code == expected_status_code
        assert expected_error_message in str(exc_info.value.detail)


@pytest.mark.unit
class TestMessageTemplateService:
    """Тесты сервиса MessageTemplateService для Bot API."""

    @pytest.mark.asyncio
    async def test_get_default_template_success(self, db: AsyncSession):
        """Тест успешного получения шаблона по умолчанию."""
        # Arrange
        expected_placeholder = "{first_name}"
        required_attributes = ["id", "name", "message_template"]

        # Act
        result = await message_template_service.get_default_template(db)

        # Assert
        assert result is not None
        for attr in required_attributes:
            assert hasattr(result, attr)
        assert expected_placeholder in result.message_template

    @pytest.mark.asyncio
    async def test_personalize_message_success(self, db: AsyncSession):
        """Тест успешной персонализации сообщения."""
        # Arrange
        template = "Привет, {first_name}! Как дела?"
        first_name = "Иван"
        expected_result = "Привет, Иван! Как дела?"

        # Act
        result = message_template_service.personalize_message(template, first_name)

        # Assert
        assert result == expected_result
        assert "{first_name}" not in result

    @pytest.mark.asyncio
    async def test_personalize_message_no_placeholder(self, db: AsyncSession):
        """Тест персонализации сообщения без плейсхолдера."""
        # Arrange
        template = "Привет! Как дела?"
        first_name = "Иван"

        # Act
        result = message_template_service.personalize_message(template, first_name)

        # Assert
        assert result == template  # Без изменений

    @pytest.mark.asyncio
    async def test_get_default_template_response_success(self, db: AsyncSession):
        """Тест успешного получения ответа с шаблоном по умолчанию для Bot API."""
        # Arrange
        expected_placeholder = "{first_name}"
        required_attributes = ["id", "name", "message_template", "created_at"]

        # Act
        result = await message_template_service.get_default_template_response(db)

        # Assert
        assert isinstance(result, BotMessageTemplateResponse)
        for attr in required_attributes:
            assert hasattr(result, attr)
        assert expected_placeholder in result.message_template
