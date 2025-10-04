"""Тесты управления Telegram пользователями."""

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.telegram_user import TelegramUser
from backend.services.telegram_user import TelegramUserService
from backend.validators.telegram_user import TelegramUserValidator


@pytest.mark.unit
class TestTelegramUserAPI:
    """Тесты API эндпоинтов для управления пользователями Telegram."""

    @pytest.mark.asyncio
    async def test_get_telegram_users_success(
        self, async_client: AsyncClient, admin_token: str, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест успешного получения списка пользователей Telegram."""
        # Arrange
        endpoint = "/api/v1/admin/telegram-users/"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 200
        expected_min_users = len(telegram_users_fixture)

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= expected_min_users

        # Проверить структуру первого пользователя
        if data["items"]:
            user = data["items"][0]
            required_fields = ["id", "telegram_id", "first_name", "subscription_type", "activities_count", "questions_count"]
            for field in required_fields:
                assert field in user

    @pytest.mark.asyncio
    async def test_get_telegram_users_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест получения списка пользователей без авторизации."""
        # Arrange
        endpoint = "/api/v1/admin/telegram-users/"
        expected_status_code = 403

        # Act
        response = await async_client_no_auth.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_telegram_users_invalid_token(self, async_client_no_auth: AsyncClient):
        """Тест получения списка пользователей с некорректным токеном."""
        # Arrange
        endpoint = "/api/v1/admin/telegram-users/"
        headers = {"Authorization": "Bearer invalid_token"}
        expected_status_code = 401

        # Act
        response = await async_client_no_auth.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_telegram_user_by_id_success(
        self, async_client: AsyncClient, admin_token: str, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест успешного получения пользователя по ID."""
        # Arrange
        user_id = telegram_users_fixture[0].id
        endpoint = f"/api/v1/admin/telegram-users/{user_id}/"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 200

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code
        user = response.json()
        
        assert user["id"] == user_id
        assert user["telegram_id"] == telegram_users_fixture[0].telegram_id
        assert user["first_name"] == telegram_users_fixture[0].first_name
        assert user["username"] == telegram_users_fixture[0].username
        assert user["activities_count"] == telegram_users_fixture[0].activities_count
        assert user["questions_count"] == telegram_users_fixture[0].questions_count

    @pytest.mark.asyncio
    async def test_get_telegram_user_by_id_not_found(self, async_client: AsyncClient, admin_token: str):
        """Тест получения несуществующего пользователя по ID."""
        # Arrange
        non_existent_id = 99999
        endpoint = f"/api/v1/admin/telegram-users/{non_existent_id}/"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 404
        expected_error_message = "Пользователь не найден"

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["error"]["message"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("invalid_id", ["abc", -1, 0])
    async def test_get_telegram_user_by_id_invalid_param(self, async_client: AsyncClient, admin_token: str, invalid_id):
        """Тест получения пользователя с некорректным ID параметром."""
        # Arrange
        endpoint = f"/api/v1/admin/telegram-users/{invalid_id}/"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 422

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_telegram_user_by_id_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест получения пользователя по ID без авторизации."""
        # Arrange
        endpoint = "/api/v1/admin/telegram-users/1/"
        expected_status_code = 403

        # Act
        response = await async_client_no_auth.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code


@pytest.mark.unit
class TestTelegramUserService:
    """Тесты сервиса TelegramUserService."""

    @pytest.mark.asyncio
    async def test_get_all_users_success(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест успешного получения всех пользователей."""
        # Arrange
        service = TelegramUserService()
        expected_min_users = len(telegram_users_fixture)

        # Act
        result = await service.get_all_users(db)

        # Assert
        assert len(result.items) >= expected_min_users
        assert isinstance(result.items, list)

        # Проверить структуру первого пользователя
        if result.items:
            user = result.items[0]
            required_attributes = ["id", "telegram_id", "first_name", "subscription_type", "activities_count", "questions_count"]
            for attr in required_attributes:
                assert hasattr(user, attr)

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест успешного получения пользователя по ID."""
        # Arrange
        service = TelegramUserService()
        user_id = telegram_users_fixture[0].id
        expected_user = telegram_users_fixture[0]

        # Act
        result = await service.get_user_by_id(user_id, db)

        # Assert
        assert result.id == user_id
        assert result.telegram_id == expected_user.telegram_id
        assert result.first_name == expected_user.first_name
        assert result.username == expected_user.username
        assert result.activities_count == expected_user.activities_count
        assert result.questions_count == expected_user.questions_count

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, db: AsyncSession):
        """Тест получения несуществующего пользователя по ID."""
        # Arrange
        service = TelegramUserService()
        non_existent_id = 99999
        expected_error_message = "Пользователь не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.get_user_by_id(non_existent_id, db)

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_activity(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест обновления времени последней активности пользователя."""
        # Arrange
        service = TelegramUserService()
        telegram_id = telegram_users_fixture[0].telegram_id
        old_activity = telegram_users_fixture[0].last_activity

        # Act
        await service.update_user_activity(db, telegram_id)

        # Assert
        updated_user = await db.get(TelegramUser, telegram_users_fixture[0].id)
        assert updated_user.last_activity != old_activity
        assert updated_user.last_activity is not None

    @pytest.mark.asyncio
    async def test_increment_user_activities_count(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест увеличения счетчика активностей пользователя."""
        # Arrange
        service = TelegramUserService()
        telegram_user_id = telegram_users_fixture[0].id
        old_count = telegram_users_fixture[0].activities_count
        increment = 3
        expected_count = old_count + increment

        # Act
        await service.increment_user_activities_count(db, telegram_user_id, increment)

        # Assert
        updated_user = await db.get(TelegramUser, telegram_user_id)
        assert updated_user.activities_count == expected_count

    @pytest.mark.asyncio
    async def test_increment_user_questions_count(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест увеличения счетчика вопросов пользователя."""
        # Arrange
        service = TelegramUserService()
        telegram_user_id = telegram_users_fixture[0].id
        old_count = telegram_users_fixture[0].questions_count
        increment = 2
        expected_count = old_count + increment

        # Act
        await service.increment_user_questions_count(db, telegram_user_id, increment)

        # Assert
        updated_user = await db.get(TelegramUser, telegram_user_id)
        assert updated_user.questions_count == expected_count


@pytest.mark.unit
class TestTelegramUserCRUD:
    """Тесты CRUD операций для TelegramUserCRUD."""

    @pytest.mark.asyncio
    async def test_get_by_telegram_id_success(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], telegram_user_crud):
        """Тест успешного получения пользователя по Telegram ID."""
        # Arrange
        telegram_id = telegram_users_fixture[0].telegram_id
        expected_user = telegram_users_fixture[0]

        # Act
        result = await telegram_user_crud.get_by_telegram_id(db, telegram_id)

        # Assert
        assert result is not None
        assert result.telegram_id == telegram_id
        assert result.id == expected_user.id

    @pytest.mark.asyncio
    async def test_get_by_telegram_id_not_found(self, db: AsyncSession, telegram_user_crud):
        """Тест получения несуществующего пользователя по Telegram ID."""
        # Arrange
        non_existent_telegram_id = 999999999

        # Act
        result = await telegram_user_crud.get_by_telegram_id(db, non_existent_telegram_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_users(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], telegram_user_crud):
        """Тест получения всех пользователей."""
        # Arrange
        expected_min_users = len(telegram_users_fixture)

        # Act
        result = await telegram_user_crud.get_all_users(db)

        # Assert
        assert isinstance(result, list)
        assert len(result) >= expected_min_users

    @pytest.mark.asyncio
    async def test_upsert_user_create_new(self, db: AsyncSession, telegram_user_crud):
        """Тест создания нового пользователя через upsert."""
        # Arrange
        telegram_id = 444444444
        first_name = "New"
        last_name = "User"
        username = "newuser"
        expected_subscription_type = "free"

        # Act
        result = await telegram_user_crud.upsert_user(
            db=db,
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )

        # Assert
        assert result.telegram_id == telegram_id
        assert result.first_name == first_name
        assert result.last_name == last_name
        assert result.username == username
        assert result.subscription_type == expected_subscription_type

    @pytest.mark.asyncio
    async def test_upsert_user_update_existing(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], telegram_user_crud):
        """Тест обновления существующего пользователя через upsert."""
        # Arrange
        existing_user = telegram_users_fixture[0]
        new_first_name = "Updated"
        new_username = "updateduser"

        # Act
        result = await telegram_user_crud.upsert_user(
            db=db,
            telegram_id=existing_user.telegram_id,
            first_name=new_first_name,
            last_name=existing_user.last_name,
            username=new_username,
        )

        # Assert
        assert result.id == existing_user.id
        assert result.telegram_id == existing_user.telegram_id
        assert result.first_name == new_first_name
        assert result.username == new_username

    @pytest.mark.asyncio
    async def test_update_last_activity(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], telegram_user_crud):
        """Тест обновления времени последней активности."""
        # Arrange
        telegram_id = telegram_users_fixture[0].telegram_id
        new_activity = datetime.now(timezone.utc)

        # Act
        await telegram_user_crud.update_last_activity(db=db, telegram_id=telegram_id, last_activity=new_activity)

        # Assert
        updated_user = await db.get(TelegramUser, telegram_users_fixture[0].id)
        assert updated_user.last_activity is not None
        # Сравниваем время без учета timezone
        time_diff = abs((updated_user.last_activity.replace(tzinfo=None) - new_activity.replace(tzinfo=None)).total_seconds())
        assert time_diff < 1

    @pytest.mark.asyncio
    async def test_increment_activities_count(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], telegram_user_crud):
        """Тест увеличения счетчика активностей."""
        # Arrange
        telegram_user_id = telegram_users_fixture[0].id
        old_count = telegram_users_fixture[0].activities_count
        increment = 5
        expected_count = old_count + increment

        # Act
        await telegram_user_crud.increment_activities_count(db=db, telegram_user_id=telegram_user_id, increment=increment)

        # Assert
        updated_user = await db.get(TelegramUser, telegram_user_id)
        assert updated_user.activities_count == expected_count

    @pytest.mark.asyncio
    async def test_increment_questions_count(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], telegram_user_crud):
        """Тест увеличения счетчика вопросов."""
        # Arrange
        telegram_user_id = telegram_users_fixture[0].id
        old_count = telegram_users_fixture[0].questions_count
        increment = 7
        expected_count = old_count + increment

        # Act
        await telegram_user_crud.increment_questions_count(db=db, telegram_user_id=telegram_user_id, increment=increment)

        # Assert
        updated_user = await db.get(TelegramUser, telegram_user_id)
        assert updated_user.questions_count == expected_count

    @pytest.mark.asyncio
    async def test_update_reminder_sent_status(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], telegram_user_crud):
        """Тест обновления статуса отправки напоминания."""
        # Arrange
        telegram_user_id = telegram_users_fixture[0].id
        sent_at = datetime.now(timezone.utc)

        # Act
        await telegram_user_crud.update_reminder_sent_status(db=db, telegram_user_id=telegram_user_id, sent_at=sent_at)

        # Assert
        updated_user = await db.get(TelegramUser, telegram_user_id)
        assert updated_user.reminder_sent_at is not None
        # Сравниваем время без учета timezone
        time_diff = abs((updated_user.reminder_sent_at.replace(tzinfo=None) - sent_at.replace(tzinfo=None)).total_seconds())
        assert time_diff < 1


@pytest.mark.unit
class TestTelegramUserValidator:
    """Тесты валидатора TelegramUserValidator."""

    def test_validate_telegram_id_success(self):
        """Тест успешной валидации корректного telegram_id."""
        # Arrange
        validator = TelegramUserValidator()
        valid_telegram_ids = [123456789, 1000, 999999999]

        # Act & Assert
        for telegram_id in valid_telegram_ids:
            # Не должно вызывать исключений
            validator.validate_telegram_id(telegram_id)

    @pytest.mark.parametrize(
        "invalid_telegram_id",
        [
            None,
            "123456789",  # строка вместо числа
            -1,  # отрицательное число
            0,  # ноль
            999,  # слишком маленькое число
        ],
    )
    def test_validate_telegram_id_invalid(self, invalid_telegram_id):
        """Тест валидации некорректных telegram_id."""
        # Arrange
        validator = TelegramUserValidator()

        # Act & Assert
        with pytest.raises(Exception):
            validator.validate_telegram_id(invalid_telegram_id)

    def test_validate_user_exists_success(self, telegram_users_fixture: list[TelegramUser]):
        """Тест успешной валидации существующего пользователя."""
        # Arrange
        validator = TelegramUserValidator()
        existing_user = telegram_users_fixture[0]

        # Act & Assert
        # Не должно вызывать исключений
        validator.validate_user_exists(existing_user)

    def test_validate_user_exists_none(self):
        """Тест валидации несуществующего пользователя (None)."""
        # Arrange
        validator = TelegramUserValidator()
        expected_error_message = "Пользователь не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validator.validate_user_exists(None)

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.parametrize("valid_user_id", [1, 100, 999999])
    def test_validate_user_id_success(self, valid_user_id):
        """Тест успешной валидации корректных ID пользователей."""
        # Arrange
        validator = TelegramUserValidator()

        # Act & Assert
        # Не должно вызывать исключений
        validator.validate_user_id(valid_user_id)

    @pytest.mark.parametrize("invalid_user_id", [0, -1, -100])
    def test_validate_user_id_invalid(self, invalid_user_id):
        """Тест валидации некорректных ID пользователей."""
        # Arrange
        validator = TelegramUserValidator()
        expected_error_message = "ID пользователя должен быть положительным числом"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validator.validate_user_id(invalid_user_id)

        assert expected_error_message in str(exc_info.value)
