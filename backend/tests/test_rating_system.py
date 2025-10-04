"""Тесты системы оценок материалов."""

import pytest
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.enums import ActivityType
from backend.models.menu_item import MenuItem
from backend.models.telegram_user import TelegramUser
from backend.schemas.public.ratings import RatingRequest
from backend.services.ratings import RatingService
from backend.validators.user_activity import UserActivityValidator


@pytest.mark.unit
class TestPublicRatingsAPI:
    """Тесты API эндпоинтов для оценок материалов."""

    @pytest.mark.asyncio
    async def test_rate_material_success(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешной оценки материала."""
        # Arrange
        endpoint = "/api/v1/public/ratings"
        user = telegram_users_fixture[0]
        menu_item = next(item for item in menu_items_fixture if item.item_type == "content")
        rating_data = {
            "telegram_user_id": user.telegram_id,
            "menu_item_id": menu_item.id,
            "rating": 5
        }
        expected_status_code = 201

        # Act
        response = await async_client.post(endpoint, json=rating_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert "message" in data
        assert "успешно" in data["message"]

    @pytest.mark.asyncio
    async def test_rate_material_user_not_found(self, async_client: AsyncClient):
        """Тест оценки материала несуществующим пользователем."""
        # Arrange
        endpoint = "/api/v1/public/ratings"
        rating_data = {
            "telegram_user_id": 999999999,
            "menu_item_id": 1,
            "rating": 4
        }
        expected_status_code = 404

        # Act
        response = await async_client.post(endpoint, json=rating_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_rate_material_menu_item_not_found(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест оценки несуществующего материала."""
        # Arrange
        endpoint = "/api/v1/public/ratings"
        user = telegram_users_fixture[0]
        rating_data = {
            "telegram_user_id": user.telegram_id,
            "menu_item_id": 999,
            "rating": 3
        }
        expected_status_code = 404
        expected_error_message = "Пункт меню не найден"

        # Act
        response = await async_client.post(endpoint, json=rating_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]

    @pytest.mark.asyncio
    async def test_rate_material_invalid_rating(self, async_client: AsyncClient):
        """Тест оценки с некорректным рейтингом."""
        # Arrange
        endpoint = "/api/v1/public/ratings"
        rating_data = {
            "telegram_user_id": 123456789,
            "menu_item_id": 1,
            "rating": 6,  # Рейтинг должен быть от 1 до 5
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=rating_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_rate_material_rating_zero(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест оценки с рейтингом 0."""
        # Arrange
        endpoint = "/api/v1/public/ratings"
        user = telegram_users_fixture[0]
        menu_item = next(item for item in menu_items_fixture if item.item_type == "content")
        rating_data = {
            "telegram_user_id": user.telegram_id,
            "menu_item_id": menu_item.id,
            "rating": 0
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=rating_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_rate_material_negative_rating(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест оценки с отрицательным рейтингом."""
        # Arrange
        endpoint = "/api/v1/public/ratings"
        user = telegram_users_fixture[0]
        menu_item = next(item for item in menu_items_fixture if item.item_type == "content")
        rating_data = {
            "telegram_user_id": user.telegram_id,
            "menu_item_id": menu_item.id,
            "rating": -1
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=rating_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_rate_material_rating_too_high(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест оценки с рейтингом выше 5."""
        # Arrange
        endpoint = "/api/v1/public/ratings"
        user = telegram_users_fixture[0]
        menu_item = next(item for item in menu_items_fixture if item.item_type == "content")
        rating_data = {
            "telegram_user_id": user.telegram_id,
            "menu_item_id": menu_item.id,
            "rating": 10
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=rating_data)

        # Assert
        assert response.status_code == expected_status_code


@pytest.mark.unit
class TestRatingService:
    """Тесты сервиса RatingService."""

    @pytest.mark.asyncio
    async def test_rate_material_success(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешной оценки материала."""
        # Arrange
        service = RatingService()
        user = telegram_users_fixture[0]
        menu_item = next(item for item in menu_items_fixture if item.item_type == "content")
        rating_data = RatingRequest(
            telegram_user_id=user.telegram_id,
            menu_item_id=menu_item.id,
            rating=5
        )
        expected_rating = 5
        expected_message = "Оценка успешно сохранена"

        # Act
        result = await service.rate_material(rating_data, db)

        # Assert
        assert result.rating == expected_rating
        assert result.message == expected_message

    @pytest.mark.asyncio
    async def test_rate_material_user_not_found(self, db: AsyncSession):
        """Тест оценки материала несуществующим пользователем."""
        # Arrange
        service = RatingService()
        rating_data = RatingRequest(
            telegram_user_id=999999999,
            menu_item_id=1,
            rating=4
        )
        expected_error_message = "Пользователь не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.rate_material(rating_data, db)

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_material_menu_item_not_found(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест оценки несуществующего материала."""
        # Arrange
        service = RatingService()
        user = telegram_users_fixture[0]
        rating_data = RatingRequest(
            telegram_user_id=user.telegram_id,
            menu_item_id=999,
            rating=3
        )
        expected_error_message = "Пункт меню не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.rate_material(rating_data, db)

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_material_inactive_menu_item(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест оценки неактивного материала."""
        # Arrange
        service = RatingService()
        user = telegram_users_fixture[0]
        inactive_item = next(item for item in menu_items_fixture if not item.is_active)
        rating_data = RatingRequest(
            telegram_user_id=user.telegram_id,
            menu_item_id=inactive_item.id,
            rating=4
        )
        expected_error_message = "неактивен"
        expected_status_code = 403

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.rate_material(rating_data, db)

        assert expected_error_message in str(exc_info.value).lower()
        # Проверяем, что это HTTPException с кодом 403
        assert hasattr(exc_info.value, 'status_code')
        assert exc_info.value.status_code == expected_status_code


@pytest.mark.unit
class TestUserActivityCRUD:
    """Тесты CRUD операций для UserActivity."""

    @pytest.mark.asyncio
    async def test_create_activity_navigation(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест создания активности типа navigation."""
        # Arrange
        from backend.crud.user_activity import user_activity_crud
        user = telegram_users_fixture[0]
        menu_item = menu_items_fixture[0]
        activity_type = ActivityType.NAVIGATION

        # Act
        result = await user_activity_crud.create_activity(
            db=db,
            telegram_user_id=user.id,
            menu_item_id=menu_item.id,
            activity_type=activity_type
        )

        # Assert
        assert result.telegram_user_id == user.id
        assert result.menu_item_id == menu_item.id
        assert result.activity_type == activity_type
        assert result.search_query is None
        assert result.rating is None

    @pytest.mark.asyncio
    async def test_create_activity_rating(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест создания активности типа rating."""
        # Arrange
        from backend.crud.user_activity import user_activity_crud
        user = telegram_users_fixture[0]
        menu_item = next(item for item in menu_items_fixture if item.item_type == "content")
        activity_type = ActivityType.RATING
        rating = 4

        # Act
        result = await user_activity_crud.create_activity(
            db=db,
            telegram_user_id=user.id,
            menu_item_id=menu_item.id,
            activity_type=activity_type,
            rating=rating
        )

        # Assert
        assert result.telegram_user_id == user.id
        assert result.menu_item_id == menu_item.id
        assert result.activity_type == activity_type
        assert result.rating == rating

    @pytest.mark.asyncio
    async def test_create_activity_search(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест создания активности типа search."""
        # Arrange
        from backend.crud.user_activity import user_activity_crud
        user = telegram_users_fixture[0]
        activity_type = ActivityType.SEARCH
        search_query = "test query"

        # Act
        result = await user_activity_crud.create_activity(
            db=db,
            telegram_user_id=user.id,
            menu_item_id=None,
            activity_type=activity_type,
            search_query=search_query,
        )

        # Assert
        assert result.telegram_user_id == user.id
        assert result.menu_item_id is None
        assert result.activity_type == activity_type
        assert result.search_query == search_query
        assert result.rating is None

    @pytest.mark.asyncio
    async def test_get_user_activities(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест получения активностей пользователя."""
        # Arrange
        from backend.crud.user_activity import user_activity_crud
        user = telegram_users_fixture[0]
        menu_item1 = menu_items_fixture[0]
        menu_item2 = menu_items_fixture[1] if len(menu_items_fixture) > 1 else menu_items_fixture[0]
        limit = 10

        # Создаем несколько активностей
        await user_activity_crud.create_activity(
            db=db,
            telegram_user_id=user.id,
            menu_item_id=menu_item1.id,
            activity_type=ActivityType.NAVIGATION
        )
        await user_activity_crud.create_activity(
            db=db,
            telegram_user_id=user.id,
            menu_item_id=menu_item2.id,
            activity_type=ActivityType.NAVIGATION
        )

        # Act
        activities = await user_activity_crud.get_user_activities(db, user.id, limit=limit)

        # Assert
        assert len(activities) >= 2
        assert all(activity.telegram_user_id == user.id for activity in activities)
        # Проверяем, что результаты отсортированы по времени создания (новые сначала)
        for i in range(len(activities) - 1):
            assert activities[i].created_at >= activities[i + 1].created_at

    @pytest.mark.asyncio
    async def test_get_menu_activities(
        self, db: AsyncSession, menu_items_fixture: list[MenuItem], telegram_users_fixture: list[TelegramUser]
    ):
        """Тест получения активностей по пункту меню."""
        # Arrange
        from backend.crud.user_activity import user_activity_crud
        menu_item = menu_items_fixture[0]
        user1 = telegram_users_fixture[0]
        user2 = telegram_users_fixture[1]
        limit = 10

        # Создаем активности для одного пункта меню от разных пользователей
        await user_activity_crud.create_activity(
            db=db,
            telegram_user_id=user1.id,
            menu_item_id=menu_item.id,
            activity_type=ActivityType.NAVIGATION
        )
        await user_activity_crud.create_activity(
            db=db,
            telegram_user_id=user2.id,
            menu_item_id=menu_item.id,
            activity_type=ActivityType.RATING,
            rating=5
        )

        # Act
        activities = await user_activity_crud.get_menu_activities(db, menu_item.id, limit=limit)

        # Assert
        assert len(activities) >= 2
        assert all(activity.menu_item_id == menu_item.id for activity in activities)
        # Проверяем, что есть разные типы активностей
        activity_types = [activity.activity_type for activity in activities]
        assert ActivityType.NAVIGATION in activity_types
        assert ActivityType.RATING in activity_types


@pytest.mark.unit
class TestUserActivityValidator:
    """Тесты валидатора UserActivityValidator."""

    def test_validate_user_exists_success(self, telegram_users_fixture: list[TelegramUser]):
        """Тест успешной валидации существующего пользователя."""
        # Arrange
        validator = UserActivityValidator()
        existing_user = telegram_users_fixture[0]

        # Act & Assert
        # Не должно вызывать исключений
        validator.validate_user_exists(existing_user)

    def test_validate_user_exists_none(self):
        """Тест валидации несуществующего пользователя (None)."""
        # Arrange
        validator = UserActivityValidator()
        expected_error_message = "Пользователь не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validator.validate_user_exists(None)

        assert expected_error_message in str(exc_info.value)

    def test_validate_menu_item_exists_success(self):
        """Тест успешной валидации существующего пункта меню."""
        # Arrange
        validator = UserActivityValidator()
        mock_menu_item = type("MockMenuItem", (), {"id": 1, "title": "Test"})()

        # Act & Assert
        # Не должно вызывать исключений
        validator.validate_menu_item_exists(mock_menu_item)

    def test_validate_menu_item_exists_none(self):
        """Тест валидации несуществующего пункта меню (None)."""
        # Arrange
        validator = UserActivityValidator()
        expected_error_message = "Пункт меню не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validator.validate_menu_item_exists(None)

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.parametrize(
        "valid_query",
        [
            "test",
            "test query",
            "a" * 2,  # Минимальная длина
            "test query with spaces",
            "русский текст",
            "ABCDEFGHIJ" * 10,  # Максимальная длина без повторений
        ],
    )
    def test_validate_search_query_success(self, valid_query):
        """Тест успешной валидации корректных поисковых запросов."""
        # Arrange
        validator = UserActivityValidator()

        # Act & Assert
        # Не должно вызывать исключений
        validator.validate_search_query(valid_query)

    def test_validate_search_query_none(self):
        """Тест валидации пустого поискового запроса (None)."""
        # Arrange
        validator = UserActivityValidator()

        # Act & Assert
        # None должен проходить валидацию без исключений
        validator.validate_search_query(None)

    @pytest.mark.parametrize(
        "invalid_query, expected_error",
        [
            ("a", "от 2 до 100 символов"),
            ("", "от 2 до 100 символов"),
            (" ", "от 2 до 100 символов"),
            ("a" * 101, "от 2 до 100 символов"),
            ("test<", "недопустимые символы"),
            ("test>", "недопустимые символы"),
            ("test{", "недопустимые символы"),
            ("test}", "недопустимые символы"),
            ("test[", "недопустимые символы"),
            ("test]", "недопустимые символы"),
            ("test\\", "недопустимые символы"),
            ("test|", "недопустимые символы"),
            ("test`", "недопустимые символы"),
            ("aaaab", "слишком много повторяющихся"),
            ("bbbbb", "слишком много повторяющихся"),
            ("11112222", "слишком много повторяющихся"),
        ],
    )
    def test_validate_search_query_invalid(self, invalid_query, expected_error):
        """Тест валидации некорректных поисковых запросов."""
        # Arrange
        validator = UserActivityValidator()

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validator.validate_search_query(invalid_query)

        assert expected_error in str(exc_info.value)

    @pytest.mark.parametrize("valid_rating", [1, 2, 3, 4, 5])
    def test_validate_rating_success_for_rating_activity(self, valid_rating):
        """Тест успешной валидации корректных рейтингов для RATING активности."""
        # Arrange
        validator = UserActivityValidator()
        activity_type = ActivityType.RATING

        # Act & Assert
        # Не должно вызывать исключений - валидация выполняется на уровне Pydantic
        validator.validate_rating(valid_rating, activity_type)

    def test_validate_rating_none_for_non_rating_activity(self):
        """Тест валидации None рейтинга для не-rating активности."""
        # Arrange
        validator = UserActivityValidator()
        navigation_activity = ActivityType.NAVIGATION
        search_activity = ActivityType.SEARCH

        # Act & Assert
        # Не должно вызывать исключений
        validator.validate_rating(None, navigation_activity)
        validator.validate_rating(None, search_activity)

    @pytest.mark.parametrize("invalid_rating", [0, -1, 6, 10])
    def test_validate_rating_range_pydantic_validation(self, invalid_rating):
        """Тест валидации диапазона рейтинга на уровне Pydantic схемы."""
        # Arrange
        telegram_user_id = 123456789
        menu_item_id = 1

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RatingRequest(
                telegram_user_id=telegram_user_id,
                menu_item_id=menu_item_id,
                rating=invalid_rating
            )

    @pytest.mark.parametrize("rating", [1, 2, 3, 4, 5])
    def test_validate_rating_provided_for_non_rating_activity(self, rating):
        """Тест валидации рейтинга для не-rating активности."""
        # Arrange
        validator = UserActivityValidator()
        activity_type = ActivityType.NAVIGATION
        expected_error_message = "только для типа активности"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validator.validate_rating(rating, activity_type)

        assert expected_error_message in str(exc_info.value)
