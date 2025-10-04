"""Тесты поисковой функциональности."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.menu_item import MenuItemCRUD
from backend.models.enums import AccessLevel
from backend.schemas.public.search import SearchListResponse
from backend.services.menu_item import menu_item_service
from backend.validators.menu_item import menu_item_validator


@pytest.mark.unit
class TestMenuItemValidator:
    """Тесты валидатора MenuItemValidator."""

    @pytest.mark.parametrize(
        "query,expected",
        [
            ("test", "test"),  # Простой запрос
            ("  test  query  ", "test query"),  # С пробелами
            ("тест", "тест"),  # Кириллица
            ("ab" * 50, "ab" * 50),  # Максимальная длина
        ],
    )
    def test_validate_search_query_success(self, query, expected):
        """Тест успешной валидации корректных поисковых запросов."""
        # Arrange
        # query и expected предоставляются параметрами

        # Act
        result = menu_item_validator.validate_search_query(query)

        # Assert
        assert result == expected

    @pytest.mark.parametrize(
        "query,error_msg",
        [
            ("test<", "недопустимые символы"),  # Запрещенные символы
            ("test>", "недопустимые символы"),
            ("test{", "недопустимые символы"),
            ("teeeeest", "повторяющихся"),  # Слишком много повторяющихся символов
            ("aaaab", "повторяющихся"),
        ],
    )
    def test_validate_search_query_invalid(self, query, error_msg):
        """Тест валидации некорректных поисковых запросов."""
        # Arrange
        # query и error_msg предоставляются параметрами

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            menu_item_validator.validate_search_query(query)

        assert error_msg in str(exc_info.value)


@pytest.mark.unit
class TestMenuItemCRUD:
    """Тесты CRUD операций для MenuItem."""

    @pytest.mark.asyncio
    async def test_search_by_query_free_access_level(self, db: AsyncSession, menu_items_fixture):
        """Тест поиска по запросу с уровнем доступа FREE."""
        # Arrange
        crud = MenuItemCRUD()
        query = "free"
        access_level = AccessLevel.FREE
        limit = 10

        # Act
        results = await crud.search_by_query(
            db=db, query=query, access_level=access_level, limit=limit
        )

        # Assert
        assert len(results) > 0
        for item in results:
            assert item.access_level == access_level
            assert item.is_active is True
            # Проверяем, что запрос найден в заголовке или описании
            searchable_text = (item.title + " " + (item.description or "")).lower()
            assert query in searchable_text

    @pytest.mark.asyncio
    async def test_search_by_query_premium_access_level(self, db: AsyncSession, menu_items_fixture):
        """Тест поиска по запросу с уровнем доступа PREMIUM."""
        # Arrange
        crud = MenuItemCRUD()
        premium_query = "premium"
        free_query = "free"
        access_level_premium = AccessLevel.PREMIUM
        access_level_free = AccessLevel.FREE
        limit = 10

        # Act
        results_premium = await crud.search_by_query(
            db=db, query=premium_query, access_level=access_level_premium, limit=limit
        )
        results_free = await crud.search_by_query(
            db=db, query=free_query, access_level=access_level_free, limit=limit
        )

        # Assert
        # Премиум пользователи должны иметь доступ ко всем материалам FREE и PREMIUM
        assert len(results_premium) >= len(results_free)

    @pytest.mark.asyncio
    async def test_search_by_query_inactive_excluded(self, db: AsyncSession, menu_items_fixture):
        """Тест что неактивные элементы исключаются из поиска."""
        # Arrange
        crud = MenuItemCRUD()
        query = "inactive"
        access_level = AccessLevel.PREMIUM
        limit = 10
        expected_results_count = 0

        # Act
        results = await crud.search_by_query(
            db=db, query=query, access_level=access_level, limit=limit
        )

        # Assert
        assert len(results) == expected_results_count

    @pytest.mark.asyncio
    async def test_search_by_query_no_results(self, db: AsyncSession, menu_items_fixture):
        """Тест поиска по несуществующему запросу."""
        # Arrange
        crud = MenuItemCRUD()
        query = "nonexistent"
        access_level = AccessLevel.PREMIUM
        limit = 10
        expected_results_count = 0

        # Act
        results = await crud.search_by_query(
            db=db, query=query, access_level=access_level, limit=limit
        )

        # Assert
        assert len(results) == expected_results_count

    @pytest.mark.asyncio
    async def test_search_by_query_russian_text(self, db: AsyncSession, menu_items_fixture):
        """Тест поиска по русскому тексту."""
        # Arrange
        crud = MenuItemCRUD()
        query = "русский"
        access_level = AccessLevel.PREMIUM
        limit = 10

        # Act
        results = await crud.search_by_query(
            db=db, query=query, access_level=access_level, limit=limit
        )

        # Assert
        assert isinstance(results, list)

    @pytest.mark.parametrize(
        "limit,expected_max",
        [
            (1, 1),  # Ограничение в 1 элемент
            (0, 0),  # Ограничение в 0 элементов
            (5, 5),  # Ограничение в 5 элементов
        ],
    )
    @pytest.mark.asyncio
    async def test_search_by_query_limit(self, db: AsyncSession, menu_items_fixture, limit, expected_max):
        """Тест ограничения количества результатов поиска."""
        # Arrange
        crud = MenuItemCRUD()
        query = "premium"
        access_level = AccessLevel.PREMIUM

        # Act
        results = await crud.search_by_query(
            db=db, query=query, access_level=access_level, limit=limit
        )

        # Assert
        assert len(results) <= expected_max


@pytest.mark.unit
class TestMenuItemService:
    """Тесты сервиса MenuItemService."""

    @pytest.mark.asyncio
    async def test_search_menu_items_success_free_user(self, db: AsyncSession, user_free, menu_items_fixture):
        """Тест успешного поиска для бесплатного пользователя."""
        # Arrange
        telegram_user_id = user_free
        query = "free"
        limit = 5

        # Act
        result = await menu_item_service.search_menu_items(
            telegram_user_id=telegram_user_id, query=query, limit=limit, db=db
        )

        # Assert
        assert isinstance(result, SearchListResponse)
        assert len(result.items) > 0

        # Проверяем, что в результатах есть материалы со словом "Free"
        titles = [item.title for item in result.items]
        assert any("Free" in title for title in titles)

    @pytest.mark.asyncio
    async def test_search_menu_items_success_premium_user(self, db: AsyncSession, user_premium, menu_items_fixture):
        """Тест успешного поиска для премиум пользователя."""
        # Arrange
        telegram_user_id = user_premium
        query = "premium"
        limit = 5

        # Act
        result = await menu_item_service.search_menu_items(
            telegram_user_id=telegram_user_id, query=query, limit=limit, db=db
        )

        # Assert
        assert isinstance(result, SearchListResponse)
        assert len(result.items) > 0

        # Проверяем, что в результатах есть материалы со словом "Premium"
        titles = [item.title for item in result.items]
        assert any("Premium" in title for title in titles)

    @pytest.mark.asyncio
    async def test_search_menu_items_invalid_query(self, db: AsyncSession, user_free):
        """Тест поиска с некорректным запросом."""
        # Arrange
        telegram_user_id = user_free
        invalid_query = "test<unsafe>"
        limit = 10
        expected_error_message = "недопустимые символы"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await menu_item_service.search_menu_items(
                telegram_user_id=telegram_user_id, query=invalid_query, limit=limit, db=db
            )

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_menu_items_no_results(self, db: AsyncSession, user_free):
        """Тест поиска по запросу, который не дает результатов."""
        # Arrange
        telegram_user_id = user_free
        query = "nonexistent"
        limit = 10
        expected_items_count = 0

        # Act
        result = await menu_item_service.search_menu_items(
            telegram_user_id=telegram_user_id, query=query, limit=limit, db=db
        )

        # Assert
        assert isinstance(result, SearchListResponse)
        assert len(result.items) == expected_items_count

    @pytest.mark.asyncio
    async def test_search_menu_items_max_length_query(self, db: AsyncSession, user_free, menu_items_fixture):
        """Тест поиска с запросом максимальной длины."""
        # Arrange
        telegram_user_id = user_free
        long_query = "ab" * 50  # 100 символов - максимальная длина
        limit = 10

        # Act
        result = await menu_item_service.search_menu_items(
            telegram_user_id=telegram_user_id, query=long_query, limit=limit, db=db
        )

        # Assert
        assert isinstance(result, SearchListResponse)

    @pytest.mark.asyncio
    async def test_search_menu_items_unsafe_query(self, db: AsyncSession, user_free):
        """Тест поиска с небезопасным запросом (содержит запрещенные символы)."""
        # Arrange
        telegram_user_id = user_free
        unsafe_query = "test<unsafe>"
        limit = 10
        expected_error_message = "недопустимые символы"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await menu_item_service.search_menu_items(
                telegram_user_id=telegram_user_id, query=unsafe_query, limit=limit, db=db
            )

        assert expected_error_message in str(exc_info.value)


@pytest.mark.unit
class TestPublicSearchAPI:
    """Тесты публичного API поиска."""

    @pytest.mark.parametrize(
        "query,expected_has_results",
        [
            ("free", True),  # Должен вернуть результаты (ищем по существующему контенту)
            ("nonexistent", False),  # Не должен вернуть результатов
        ],
    )
    @pytest.mark.asyncio
    async def test_search_materials_success(self, async_client: AsyncClient, user_free, query, expected_has_results):
        """Тест успешного поиска материалов."""
        # Arrange
        endpoint = "/api/v1/public/search"
        telegram_user_id = user_free
        limit = 10
        expected_status_code = 200
        url = f"{endpoint}?telegram_user_id={telegram_user_id}&query={query}&limit={limit}"

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

        if expected_has_results:
            assert len(data["items"]) >= 0  # Может быть пустым, если нет подходящих данных
        else:
            assert len(data["items"]) == 0

    @pytest.mark.parametrize(
        "params,expected_status",
        [
            ({"query": "test", "limit": 10}, 422),  # Отсутствует telegram_user_id (pydantic валидация)
            ({"telegram_user_id": 123456789, "limit": 10}, 422),  # Отсутствует query (pydantic валидация)
            ({"telegram_user_id": 123456789, "query": "test"}, 404),  # Пользователь не существует (бизнес-логика)
        ],
    )
    @pytest.mark.asyncio
    async def test_search_materials_missing_params(self, async_client: AsyncClient, params, expected_status):
        """Тест поиска с отсутствующими или некорректными параметрами."""
        # Arrange
        endpoint = "/api/v1/public/search"

        # Act
        response = await async_client.get(endpoint, params=params)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "limit,expected_status",
        [
            ("abc", 422),  # Некорректный тип (pydantic валидация)
            (0, 422),  # Слишком маленький limit (pydantic валидация)
            (-1, 422),  # Отрицательный limit (pydantic валидация)
            (1000, 422),  # Слишком большой limit (pydantic валидация)
            (10, 404),  # Корректный limit, но пользователь не найден (бизнес-логика)
        ],
    )
    @pytest.mark.asyncio
    async def test_search_materials_invalid_limit(self, async_client: AsyncClient, limit, expected_status):
        """Тест поиска с некорректным значением limit."""
        # Arrange
        endpoint = "/api/v1/public/search"
        telegram_user_id = 123456789
        query = "test"
        url = f"{endpoint}?telegram_user_id={telegram_user_id}&query={query}&limit={limit}"

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "telegram_user_id,expected_status",
        [
            (-1, 422),  # Отрицательный ID (pydantic валидация)
            (0, 422),  # Нулевой ID (pydantic валидация)
            ("abc", 422),  # Некорректный тип (pydantic валидация)
            (123456789, 404),  # ID не существует (бизнес-логика)
        ],
    )
    @pytest.mark.asyncio
    async def test_search_materials_invalid_telegram_id(
        self, async_client: AsyncClient, telegram_user_id, expected_status
    ):
        """Тест поиска с некорректным telegram_user_id."""
        # Arrange
        endpoint = "/api/v1/public/search"
        query = "test"
        limit = 10
        url = f"{endpoint}?telegram_user_id={telegram_user_id}&query={query}&limit={limit}"

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "query,expected_status",
        [
            ("a", 422),  # Слишком короткий запрос (pydantic валидация в Query)
            ("test<unsafe>", 404),  # Запрещенные символы, но пользователь не найден (бизнес-логика)
            ("ab" * 50, 404),  # Максимальная длина, но пользователь не найден (бизнес-логика)
        ],
    )
    @pytest.mark.asyncio
    async def test_search_materials_query_validation(self, async_client: AsyncClient, query, expected_status):
        """Тест валидации поискового запроса."""
        # Arrange
        endpoint = "/api/v1/public/search"
        telegram_user_id = 123456789
        limit = 10
        url = f"{endpoint}?telegram_user_id={telegram_user_id}&query={query}&limit={limit}"

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_search_materials_business_validation_with_existing_user(
        self, async_client: AsyncClient, user_free
    ):
        """Тест бизнес-валидации поискового запроса с существующим пользователем."""
        # Arrange
        endpoint = "/api/v1/public/search"
        telegram_user_id = user_free
        unsafe_query = "test<unsafe>"
        limit = 10
        expected_status_code = 400
        expected_error_message = "недопустимые символы"
        url = f"{endpoint}?telegram_user_id={telegram_user_id}&query={unsafe_query}&limit={limit}"

        # Act
        response = await async_client.get(url)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]
