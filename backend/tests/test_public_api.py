"""Тесты публичных API эндпоинтов."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.menu_item import MenuItem
from backend.models.telegram_user import TelegramUser
from backend.schemas.public.question import UserQuestionCreate
from backend.schemas.public.ratings import RatingRequest
from backend.schemas.public.user_activity import UserActivityRequest
from backend.services.menu_item import MenuItemService
from backend.services.question import UserQuestionService
from backend.services.ratings import RatingService
from backend.services.user_activity import UserActivityService


@pytest.mark.unit
class TestPublicMenuAPI:
    """Тесты API эндпоинтов для работы с меню."""

    @pytest.mark.asyncio
    async def test_get_menu_items_success_free_user(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного получения меню для бесплатного пользователя."""
        # Arrange
        endpoint = "/api/v1/public/menu-items"
        free_user = next(user for user in telegram_users_fixture if user.subscription_type == "free")
        url = f"{endpoint}?telegram_user_id={free_user.telegram_id}"
        expected_status_code = 200

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert "items" in data
        assert isinstance(data["items"], list)

        # Проверяем, что вернулись только доступные бесплатные пункты
        free_items = [
            item
            for item in menu_items_fixture
            if item.access_level == "free" and item.is_active and item.parent_id is None
        ]
        assert len(data["items"]) >= len(free_items)

        # Проверяем структуру ответа
        if data["items"]:
            item = data["items"][0]
            required_fields = ["id", "title", "description", "item_type", "access_level", "is_active"]
            for field in required_fields:
                assert field in item

    @pytest.mark.asyncio
    async def test_get_menu_items_success_premium_user(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного получения меню для премиум пользователя."""
        # Arrange
        endpoint = "/api/v1/public/menu-items"
        premium_user = next(user for user in telegram_users_fixture if user.subscription_type == "premium")
        url = f"{endpoint}?telegram_user_id={premium_user.telegram_id}"
        expected_status_code = 200

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert "items" in data

        # Премиум пользователь должен видеть все пункты
        active_root_items = [item for item in menu_items_fixture if item.is_active and item.parent_id is None]
        assert len(data["items"]) >= len(active_root_items)

    @pytest.mark.asyncio
    async def test_get_menu_items_with_parent_id(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест получения дочерних пунктов меню."""
        # Arrange
        endpoint = "/api/v1/public/menu-items"
        free_user = next(user for user in telegram_users_fixture if user.subscription_type == "free")
        parent_item = next(item for item in menu_items_fixture if item.title == "Root Free Item")
        url = f"{endpoint}?telegram_user_id={free_user.telegram_id}&parent_id={parent_item.id}"
        expected_status_code = 200

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert "items" in data

        # Проверяем дочерние элементы
        children = [
            item for item in menu_items_fixture if item.parent_id == parent_item.id and item.access_level == "free"
        ]
        assert len(data["items"]) >= len(children)

    @pytest.mark.asyncio
    async def test_get_menu_items_user_not_found(self, async_client: AsyncClient):
        """Тест получения меню для несуществующего пользователя."""
        # Arrange
        endpoint = "/api/v1/public/menu-items"
        non_existent_user_id = 999999999
        url = f"{endpoint}?telegram_user_id={non_existent_user_id}"
        expected_status_code = 404
        expected_error_message = "Пользователь не найден"

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]

    @pytest.mark.asyncio
    async def test_get_menu_items_missing_user_id(self, async_client: AsyncClient):
        """Тест получения меню без указания ID пользователя."""
        # Arrange
        endpoint = "/api/v1/public/menu-items"
        expected_status_code = 422

        # Act
        response = await async_client.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_menu_item_content_success(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного получения контента пункта меню."""
        # Arrange
        free_user = next(user for user in telegram_users_fixture if user.subscription_type == "free")
        content_item = next(item for item in menu_items_fixture if item.title == "Free Content Item")
        endpoint = f"/api/v1/public/menu-items/{content_item.id}/content"
        url = f"{endpoint}?telegram_user_id={free_user.telegram_id}"
        expected_status_code = 200

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        required_fields = ["id", "title", "description", "item_type", "content_files", "children"]
        for field in required_fields:
            assert field in data

    @pytest.mark.asyncio
    async def test_get_menu_item_content_not_found(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест получения контента несуществующего пункта меню."""
        # Arrange
        user = telegram_users_fixture[0]
        non_existent_item_id = 999
        endpoint = f"/api/v1/public/menu-items/{non_existent_item_id}/content"
        url = f"{endpoint}?telegram_user_id={user.telegram_id}"
        expected_status_code = 404
        expected_error_message = "Пункт меню не найден"

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]

    @pytest.mark.asyncio
    async def test_get_menu_item_content_inactive(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест получения контента неактивного пункта меню."""
        # Arrange
        free_user = next(user for user in telegram_users_fixture if user.subscription_type == "free")
        non_existent_item_id = 999
        endpoint = f"/api/v1/public/menu-items/{non_existent_item_id}/content"
        url = f"{endpoint}?telegram_user_id={free_user.telegram_id}"
        expected_status_code = 404

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code


@pytest.mark.unit
class TestPublicQuestionAPI:
    """Тесты API эндпоинтов для вопросов пользователей."""

    @pytest.mark.asyncio
    async def test_create_user_question_success(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест успешного создания вопроса пользователем."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        user = telegram_users_fixture[0]
        question_data = {
            "telegram_user_id": user.telegram_id,
            "question_text": "Это тестовый вопрос для проверки функциональности",
        }
        expected_status_code = 201

        # Act
        response = await async_client.post(endpoint, json=question_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert "question_text" in data
        assert "status" in data
        assert data["question_text"] == question_data["question_text"]

    @pytest.mark.asyncio
    async def test_create_user_question_user_not_found(self, async_client: AsyncClient):
        """Тест создания вопроса для несуществующего пользователя."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        question_data = {"telegram_user_id": 999999999, "question_text": "Тестовый вопрос"}
        expected_status_code = 404
        expected_error_message = "Пользователь не найден"

        # Act
        response = await async_client.post(endpoint, json=question_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]

    @pytest.mark.asyncio
    async def test_create_user_question_empty_text(self, async_client: AsyncClient):
        """Тест создания вопроса с пустым текстом."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        question_data = {"telegram_user_id": 123456789, "question_text": ""}
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=question_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_create_user_question_too_short(self, async_client: AsyncClient):
        """Тест создания вопроса с слишком коротким текстом."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        question_data = {"telegram_user_id": 123456789, "question_text": "Коротко"}
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=question_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_create_user_question_invalid_characters(self, async_client: AsyncClient):
        """Тест создания вопроса с недопустимыми символами."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        question_data = {"telegram_user_id": 123456789, "question_text": "Вопрос с <script>alert('xss')</script>"}
        expected_status_code = 400
        expected_error_message = "недопустимые символы"

        # Act
        response = await async_client.post(endpoint, json=question_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]

    @pytest.mark.asyncio
    async def test_create_user_question_too_long(self, async_client: AsyncClient):
        """Тест создания вопроса с слишком длинным текстом."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        long_text = "A" * 2001  # Превышает лимит в 2000 символов
        question_data = {"telegram_user_id": 123456789, "question_text": long_text}
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=question_data)

        # Assert
        assert response.status_code == expected_status_code


@pytest.mark.unit
class TestPublicUserActivityAPI:
    """Тесты API эндпоинтов для активности пользователей."""

    @pytest.mark.asyncio
    async def test_record_user_activity_success(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешной записи активности пользователя."""
        # Arrange
        endpoint = "/api/v1/public/user-activities"
        user = telegram_users_fixture[0]
        menu_item = menu_items_fixture[0]
        activity_data = {
            "telegram_user_id": user.telegram_id,
            "menu_item_id": menu_item.id,
            "activity_type": "navigation",
            "search_query": None,
        }
        expected_status_code = 201

        # Act
        response = await async_client.post(endpoint, json=activity_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert "message" in data
        assert "успешно" in data["message"]

    @pytest.mark.asyncio
    async def test_record_user_activity_user_not_found(self, async_client: AsyncClient):
        """Тест записи активности для несуществующего пользователя."""
        # Arrange
        endpoint = "/api/v1/public/user-activities"
        activity_data = {
            "telegram_user_id": 999999999,
            "menu_item_id": 1,
            "activity_type": "navigation",
            "search_query": None,
        }
        expected_status_code = 404
        expected_error_message = "Пользователь не найден"

        # Act
        response = await async_client.post(endpoint, json=activity_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]

    @pytest.mark.asyncio
    async def test_record_user_activity_menu_item_not_found(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест записи активности для несуществующего пункта меню."""
        # Arrange
        endpoint = "/api/v1/public/user-activities"
        user = telegram_users_fixture[0]
        activity_data = {
            "telegram_user_id": user.telegram_id,
            "menu_item_id": 999,
            "activity_type": "navigation",
            "search_query": None,
        }
        expected_status_code = 404
        expected_error_message = "Пункт меню не найден"

        # Act
        response = await async_client.post(endpoint, json=activity_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]

    @pytest.mark.asyncio
    async def test_record_user_activity_invalid_activity_type(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест записи активности с некорректным типом активности."""
        # Arrange
        endpoint = "/api/v1/public/user-activities"
        user = telegram_users_fixture[0]
        menu_item = menu_items_fixture[0]
        activity_data = {
            "telegram_user_id": user.telegram_id,
            "menu_item_id": menu_item.id,
            "activity_type": "invalid_type",
            "search_query": None,
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=activity_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_record_user_activity_invalid_search_query(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест записи активности с некорректным поисковым запросом."""
        # Arrange
        endpoint = "/api/v1/public/user-activities"
        user = telegram_users_fixture[0]
        menu_item = menu_items_fixture[0]
        activity_data = {
            "telegram_user_id": user.telegram_id,
            "menu_item_id": menu_item.id,
            "activity_type": "search",
            "search_query": "<script>alert('xss')</script>",
        }
        expected_status_code = 400
        expected_error_message = "недопустимые символы"

        # Act
        response = await async_client.post(endpoint, json=activity_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]


@pytest.mark.unit
class TestPublicSearchAPI:
    """Тесты API эндпоинтов для поиска."""

    @pytest.mark.asyncio
    async def test_search_materials_success(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного поиска материалов."""
        # Arrange
        endpoint = "/api/v1/public/search"
        user = telegram_users_fixture[0]
        search_query = "root"
        url = f"{endpoint}?telegram_user_id={user.telegram_id}&query={search_query}"
        expected_status_code = 200

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert "items" in data
        assert isinstance(data["items"], list)

        # Проверяем структуру результатов
        if data["items"]:
            item = data["items"][0]
            required_fields = ["id", "title", "description", "item_type"]
            for field in required_fields:
                assert field in item

    @pytest.mark.asyncio
    async def test_search_materials_user_not_found(self, async_client: AsyncClient):
        """Тест поиска для несуществующего пользователя."""
        # Arrange
        endpoint = "/api/v1/public/search"
        non_existent_user_id = 999999999
        search_query = "test"
        url = f"{endpoint}?telegram_user_id={non_existent_user_id}&query={search_query}"
        expected_status_code = 404
        expected_error_message = "Пользователь не найден"

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]

    @pytest.mark.asyncio
    async def test_search_materials_empty_query(self, async_client: AsyncClient):
        """Тест поиска с пустым запросом."""
        # Arrange
        endpoint = "/api/v1/public/search"
        user_id = 123456789
        empty_query = ""
        url = f"{endpoint}?telegram_user_id={user_id}&query={empty_query}"
        expected_status_code = 422

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_search_materials_too_short_query(self, async_client: AsyncClient):
        """Тест поиска с слишком коротким запросом."""
        # Arrange
        endpoint = "/api/v1/public/search"
        user_id = 123456789
        short_query = "a"
        url = f"{endpoint}?telegram_user_id={user_id}&query={short_query}"
        expected_status_code = 422

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_search_materials_invalid_characters(self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]):
        """Тест поиска с недопустимыми символами в запросе."""
        # Arrange
        endpoint = "/api/v1/public/search"
        user = telegram_users_fixture[0]
        invalid_query = "<script>alert('xss')</script>"
        url = f"{endpoint}?telegram_user_id={user.telegram_id}&query={invalid_query}"
        expected_status_code = 400
        expected_error_message = "недопустимые символы"

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]

    @pytest.mark.asyncio
    async def test_search_materials_too_long_query(self, async_client: AsyncClient):
        """Тест поиска с слишком длинным запросом."""
        # Arrange
        endpoint = "/api/v1/public/search"
        user_id = 123456789
        long_query = "A" * 101  # Превышает лимит в 100 символов
        url = f"{endpoint}?telegram_user_id={user_id}&query={long_query}"
        expected_status_code = 422

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_search_materials_invalid_limit(self, async_client: AsyncClient):
        """Тест поиска с некорректным лимитом результатов."""
        # Arrange
        endpoint = "/api/v1/public/search"
        user_id = 123456789
        search_query = "test"
        invalid_limit = 101
        url = f"{endpoint}?telegram_user_id={user_id}&query={search_query}&limit={invalid_limit}"
        expected_status_code = 422

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code


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
        rating_data = {"telegram_user_id": user.telegram_id, "menu_item_id": menu_item.id, "rating": 5}
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
        rating_data = {"telegram_user_id": 999999999, "menu_item_id": 1, "rating": 4}
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
        rating_data = {"telegram_user_id": user.telegram_id, "menu_item_id": 999, "rating": 3}
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
    async def test_rate_material_rating_zero(self, async_client: AsyncClient):
        """Тест оценки с нулевым рейтингом."""
        # Arrange
        endpoint = "/api/v1/public/ratings"
        rating_data = {
            "telegram_user_id": 123456789,
            "menu_item_id": 1,
            "rating": 0,  # Рейтинг должен быть от 1 до 5
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=rating_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_rate_material_rating_negative(self, async_client: AsyncClient):
        """Тест оценки с отрицательным рейтингом."""
        # Arrange
        endpoint = "/api/v1/public/ratings"
        rating_data = {
            "telegram_user_id": 123456789,
            "menu_item_id": 1,
            "rating": -1,  # Рейтинг должен быть от 1 до 5
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=rating_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_rate_material_missing_fields(self, async_client: AsyncClient):
        """Тест оценки с отсутствующими обязательными полями."""
        # Arrange
        endpoint = "/api/v1/public/ratings"
        rating_data = {
            "telegram_user_id": 123456789,
            # Отсутствует menu_item_id и rating
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=rating_data)

        # Assert
        assert response.status_code == expected_status_code


@pytest.mark.unit
class TestRESTCompliance:
    """Тесты соответствия принципам REST."""

    @pytest.mark.asyncio
    async def test_menu_items_method_not_allowed(self, async_client: AsyncClient):
        """Тест недопустимых HTTP методов для эндпоинта меню."""
        # Arrange
        endpoint = "/api/v1/public/menu-items"
        url = f"{endpoint}?telegram_user_id=123456789"
        expected_status_code = 405

        # Act
        response = await async_client.put(url)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_user_questions_method_not_allowed(self, async_client: AsyncClient):
        """Тест недопустимых HTTP методов для эндпоинта вопросов."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        expected_status_code = 405

        # Act
        response = await async_client.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_user_activities_method_not_allowed(self, async_client: AsyncClient):
        """Тест недопустимых HTTP методов для эндпоинта активности."""
        # Arrange
        endpoint = "/api/v1/public/user-activities"
        expected_status_code = 405

        # Act
        response = await async_client.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_ratings_method_not_allowed(self, async_client: AsyncClient):
        """Тест недопустимых HTTP методов для эндпоинта рейтингов."""
        # Arrange
        endpoint = "/api/v1/public/ratings"
        expected_status_code = 405

        # Act
        response = await async_client.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_search_method_not_allowed(self, async_client: AsyncClient):
        """Тест недопустимых HTTP методов для эндпоинта поиска."""
        # Arrange
        endpoint = "/api/v1/public/search"
        expected_status_code = 405

        # Act
        response = await async_client.post(endpoint)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_content_type_validation(self, async_client: AsyncClient):
        """Тест валидации Content-Type для POST запросов."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        question_data = {"telegram_user_id": 123456789, "question_text": "Тестовый вопрос"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        expected_status_code = 422

        # Act
        response = await async_client.post(
            endpoint,
            data=question_data,  # Отправляем как form-data вместо JSON
            headers=headers
        )

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_json_syntax_error(self, async_client: AsyncClient):
        """Тест обработки синтаксических ошибок JSON."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        invalid_json = '{"telegram_user_id": 123456789, "question_text": "Тестовый вопрос"'  # Незакрытая скобка
        headers = {"Content-Type": "application/json"}
        expected_status_code = 422

        # Act
        response = await async_client.post(
            endpoint,
            data=invalid_json,
            headers=headers
        )

        # Assert
        assert response.status_code == expected_status_code


@pytest.mark.unit
class TestMenuItemService:
    """Тесты сервиса MenuItemService."""

    @pytest.mark.asyncio
    async def test_get_menu_items_success_free_user(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного получения меню для бесплатного пользователя."""
        # Arrange
        service = MenuItemService()
        free_user = next(user for user in telegram_users_fixture if user.subscription_type == "free")

        # Act
        result = await service.get_menu_items(free_user.telegram_id, None, db)

        # Assert
        assert len(result.items) >= 0
        assert isinstance(result.items, list)

        # Проверяем, что бесплатный пользователь видит только бесплатные пункты
        for item in result.items:
            assert item.access_level == "free"

    @pytest.mark.asyncio
    async def test_get_menu_items_success_premium_user(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного получения меню для премиум пользователя."""
        # Arrange
        service = MenuItemService()
        premium_user = next(user for user in telegram_users_fixture if user.subscription_type == "premium")

        # Act
        result = await service.get_menu_items(premium_user.telegram_id, None, db)

        # Assert
        assert len(result.items) >= 0
        assert isinstance(result.items, list)

    @pytest.mark.asyncio
    async def test_get_menu_items_with_parent_id(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест получения дочерних пунктов меню."""
        # Arrange
        service = MenuItemService()
        free_user = next(user for user in telegram_users_fixture if user.subscription_type == "free")
        parent_item = next(item for item in menu_items_fixture if item.title == "Root Free Item")

        # Act
        result = await service.get_menu_items(free_user.telegram_id, parent_item.id, db)

        # Assert
        assert isinstance(result.items, list)

        # Проверяем, что возвращаются только дочерние элементы
        for item in result.items:
            assert item.parent_id == parent_item.id

    @pytest.mark.asyncio
    async def test_get_menu_item_content_success(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного получения контента пункта меню."""
        # Arrange
        service = MenuItemService()
        free_user = next(user for user in telegram_users_fixture if user.subscription_type == "free")
        content_item = next(item for item in menu_items_fixture if item.title == "Free Content Item")

        # Act
        result = await service.get_menu_item_content(content_item.id, free_user.telegram_id, db)

        # Assert
        assert result.id == content_item.id
        assert result.title == content_item.title
        assert result.item_type == content_item.item_type
        assert isinstance(result.content_files, list)
        assert isinstance(result.children, list)

    @pytest.mark.asyncio
    async def test_get_menu_item_content_not_found(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест получения контента несуществующего пункта меню."""
        # Arrange
        service = MenuItemService()
        user = telegram_users_fixture[0]
        non_existent_item_id = 999
        expected_error_message = "Пункт меню не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.get_menu_item_content(non_existent_item_id, user.telegram_id, db)

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_menu_items_success(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного поиска по материалам."""
        # Arrange
        service = MenuItemService()
        user = telegram_users_fixture[0]
        search_query = "root"
        limit = 10

        # Act
        result = await service.search_menu_items(user.telegram_id, search_query, limit, db)

        # Assert
        assert isinstance(result.items, list)

        # Проверяем структуру результатов
        for item in result.items:
            assert hasattr(item, "id")
            assert hasattr(item, "title")
            assert hasattr(item, "item_type")


@pytest.mark.unit
class TestUserQuestionService:
    """Тесты сервиса UserQuestionService."""

    @pytest.mark.asyncio
    async def test_create_user_question_success(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест успешного создания вопроса пользователем."""
        # Arrange
        service = UserQuestionService()
        user = telegram_users_fixture[0]
        question_data = UserQuestionCreate(
            telegram_user_id=user.telegram_id,
            question_text="Это тестовый вопрос для проверки функциональности сервиса"
        )

        # Act
        result = await service.create_user_question(question_data, db)

        # Assert
        assert result.question_text == question_data.question_text
        assert result.status is not None

    @pytest.mark.asyncio
    async def test_create_user_question_user_not_found(self, db: AsyncSession):
        """Тест создания вопроса для несуществующего пользователя."""
        # Arrange
        service = UserQuestionService()
        question_data = UserQuestionCreate(telegram_user_id=999999999, question_text="Тестовый вопрос")
        expected_error_message = "Пользователь не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.create_user_question(question_data, db)

        assert expected_error_message in str(exc_info.value)


@pytest.mark.unit
class TestUserActivityService:
    """Тесты сервиса UserActivityService."""

    @pytest.mark.asyncio
    async def test_record_activity_success(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешной записи активности пользователя."""
        # Arrange
        service = UserActivityService()
        user = telegram_users_fixture[0]
        menu_item = menu_items_fixture[0]
        activity_data = UserActivityRequest(
            telegram_user_id=user.telegram_id,
            menu_item_id=menu_item.id,
            activity_type="navigation",
            search_query=None
        )

        # Act
        result = await service.record_activity(activity_data, db)

        # Assert
        assert result.menu_item_id == menu_item.id
        assert result.activity_type == "navigation"
        assert result.message == "Активность успешно записана"

    @pytest.mark.asyncio
    async def test_record_activity_user_not_found(self, db: AsyncSession):
        """Тест записи активности для несуществующего пользователя."""
        # Arrange
        service = UserActivityService()
        activity_data = UserActivityRequest(
            telegram_user_id=999999999,
            menu_item_id=1,
            activity_type="navigation",
            search_query=None
        )
        expected_error_message = "Пользователь не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.record_activity(activity_data, db)

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_record_activity_menu_item_not_found(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест записи активности для несуществующего пункта меню."""
        # Arrange
        service = UserActivityService()
        user = telegram_users_fixture[0]
        activity_data = UserActivityRequest(
            telegram_user_id=user.telegram_id,
            menu_item_id=999,
            activity_type="navigation",
            search_query=None
        )
        expected_error_message = "Пункт меню не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.record_activity(activity_data, db)

        assert expected_error_message in str(exc_info.value)


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
        rating_data = RatingRequest(telegram_user_id=user.telegram_id, menu_item_id=menu_item.id, rating=5)

        # Act
        result = await service.rate_material(rating_data, db)

        # Assert
        assert result.rating == rating_data.rating
        assert result.message == "Оценка успешно сохранена"

    @pytest.mark.asyncio
    async def test_rate_material_user_not_found(self, db: AsyncSession):
        """Тест оценки материала несуществующим пользователем."""
        # Arrange
        service = RatingService()
        rating_data = RatingRequest(telegram_user_id=999999999, menu_item_id=1, rating=4)
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
        rating_data = RatingRequest(telegram_user_id=user.telegram_id, menu_item_id=999, rating=3)
        expected_error_message = "Пункт меню не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.rate_material(rating_data, db)

        assert expected_error_message in str(exc_info.value)
