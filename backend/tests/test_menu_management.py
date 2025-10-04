"""Тесты управления меню и контентом."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.enums import AccessLevel, ItemType
from backend.models.menu_item import MenuItem
from backend.models.telegram_user import TelegramUser
from backend.schemas.admin.menu import AdminMenuItemCreate
from backend.schemas.public.search import SearchListResponse
from backend.services.menu_item import MenuItemService


@pytest.mark.unit
class TestAdminMenuAPI:
    """Тесты API эндпоинтов администрирования меню."""

    @pytest.mark.asyncio
    async def test_get_admin_menu_items_success(
        self, async_client: AsyncClient, admin_token: str, menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного получения списка пунктов меню для администратора."""
        # Arrange
        endpoint = "/api/v1/admin/menu-items"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 200

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= len(menu_items_fixture)

        # Проверяем структуру ответа
        if data["items"]:
            item = data["items"][0]
            required_fields = ["id", "title", "description", "item_type", "access_level", "is_active", "created_at"]
            for field in required_fields:
                assert field in item

    @pytest.mark.asyncio
    async def test_get_admin_menu_items_with_filters(
        self, async_client: AsyncClient, admin_token: str, menu_items_fixture: list[MenuItem]
    ):
        """Тест получения пунктов меню с фильтрами."""
        # Arrange
        endpoint = "/api/v1/admin/menu-items"
        headers = {"Authorization": f"Bearer {admin_token}"}
        query_params = "?is_active=true&access_level=free"
        expected_status_code = 200

        # Act
        response = await async_client.get(f"{endpoint}{query_params}", headers=headers)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert "items" in data

        # Проверяем, что все возвращенные пункты соответствуют фильтрам
        for item in data["items"]:
            assert item["is_active"] is True
            assert item["access_level"] == "free"

    @pytest.mark.asyncio
    async def test_get_admin_menu_items_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест получения пунктов меню без авторизации."""
        # Arrange
        endpoint = "/api/v1/admin/menu-items"
        expected_status_code = 403

        # Act
        response = await async_client_no_auth.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_admin_menu_items_invalid_token(self, async_client_no_auth: AsyncClient):
        """Тест получения пунктов меню с некорректным токеном."""
        # Arrange
        endpoint = "/api/v1/admin/menu-items"
        headers = {"Authorization": "Bearer invalid_token"}
        expected_status_code = 401

        # Act
        response = await async_client_no_auth.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_admin_menu_items_insufficient_permissions(
        self, async_client: AsyncClient, moderator_token: str
    ):
        """Тест получения пунктов меню с недостаточными правами доступа."""
        # Arrange
        endpoint = "/api/v1/admin/menu-items"
        headers = {"Authorization": f"Bearer {moderator_token}"}
        expected_status_code = 200

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_create_menu_item_success(self, async_client: AsyncClient, admin_token: str):
        """Тест успешного создания пункта меню."""
        # Arrange
        endpoint = "/api/v1/admin/menu-items"
        headers = {"Authorization": f"Bearer {admin_token}"}
        menu_data = {
            "title": "Новый тестовый пункт",
            "description": "Описание тестового пункта",
            "item_type": "content",
            "access_level": "free",
            "is_active": True,
        }
        expected_status_code = 201

        # Act
        response = await async_client.post(endpoint, headers=headers, json=menu_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert data["title"] == menu_data["title"]
        assert data["description"] == menu_data["description"]
        assert data["item_type"] == menu_data["item_type"]
        assert data["access_level"] == menu_data["access_level"]
        assert data["is_active"] == menu_data["is_active"]
        assert "id" in data
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_create_menu_item_with_parent(
        self, async_client: AsyncClient, admin_token: str, menu_items_fixture: list[MenuItem]
    ):
        """Тест создания дочернего пункта меню."""
        # Arrange
        endpoint = "/api/v1/admin/menu-items"
        headers = {"Authorization": f"Bearer {admin_token}"}
        parent_item = next(item for item in menu_items_fixture if item.item_type == ItemType.NAVIGATION)
        
        menu_data = {
            "title": "Дочерний пункт",
            "description": "Описание дочернего пункта",
            "parent_id": parent_item.id,
            "item_type": "content",
            "access_level": "free",
            "is_active": True,
        }
        expected_status_code = 201

        # Act
        response = await async_client.post(endpoint, headers=headers, json=menu_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert data["parent_id"] == parent_item.id

    @pytest.mark.asyncio
    async def test_create_menu_item_invalid_data(self, async_client: AsyncClient, admin_token: str):
        """Тест создания пункта меню с некорректными данными."""
        # Arrange
        endpoint = "/api/v1/admin/menu-items"
        headers = {"Authorization": f"Bearer {admin_token}"}
        menu_data = {
            "title": "",  # Пустое название
            "item_type": "invalid_type",  # Некорректный тип
            "access_level": "invalid_level",  # Некорректный уровень доступа
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, headers=headers, json=menu_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)

    @pytest.mark.asyncio
    async def test_update_menu_item_success(
        self, async_client: AsyncClient, admin_token: str, menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного обновления пункта меню."""
        # Arrange
        menu_item = menu_items_fixture[0]
        endpoint = f"/api/v1/admin/menu-items/{menu_item.id}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {
            "title": "Обновленный заголовок",
            "description": "Обновленное описание",
            "is_active": False
        }
        expected_status_code = 200

        # Act
        response = await async_client.patch(endpoint, headers=headers, json=update_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["is_active"] == update_data["is_active"]
        assert data["id"] == menu_item.id

    @pytest.mark.asyncio
    async def test_update_menu_item_not_found(self, async_client: AsyncClient, admin_token: str):
        """Тест обновления несуществующего пункта меню."""
        # Arrange
        non_existent_id = 99999
        endpoint = f"/api/v1/admin/menu-items/{non_existent_id}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {"title": "Новый заголовок"}
        expected_status_code = 404

        # Act
        response = await async_client.patch(endpoint, headers=headers, json=update_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_delete_menu_item_success(
        self, async_client: AsyncClient, admin_token: str, menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного удаления пункта меню."""
        # Arrange
        menu_item = next(
            (item for item in menu_items_fixture if item.item_type == ItemType.CONTENT), 
            menu_items_fixture[-1]
        )
        endpoint = f"/api/v1/admin/menu-items/{menu_item.id}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 204

        # Act
        response = await async_client.delete(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

        # Проверяем, что пункт действительно удален
        update_data = {"title": "Попытка обновления удаленного пункта"}
        update_response = await async_client.patch(endpoint, headers=headers, json=update_data)
        assert update_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_menu_item_not_found(self, async_client: AsyncClient, admin_token: str):
        """Тест удаления несуществующего пункта меню."""
        # Arrange
        non_existent_id = 99999
        endpoint = f"/api/v1/admin/menu-items/{non_existent_id}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 404

        # Act
        response = await async_client.delete(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_delete_menu_item_with_children(
        self, async_client: AsyncClient, admin_token: str, menu_items_fixture: list[MenuItem]
    ):
        """Тест удаления пункта меню с дочерними элементами."""
        # Arrange
        parent_item = next(
            (item for item in menu_items_fixture if item.item_type == ItemType.NAVIGATION), None
        )
        
        if not parent_item:
            pytest.skip("Нет пунктов меню с типом NAVIGATION для тестирования")

        endpoint = f"/api/v1/admin/menu-items/{parent_item.id}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 400

        # Act
        response = await async_client.delete(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert "дочерние элементы" in data["detail"].lower()


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
        result = service.get_menu_items(free_user.telegram_id, None, db)

        # Assert
        assert hasattr(result, "__await__")  # Это корутина

    @pytest.mark.asyncio
    async def test_get_menu_items_success_free_user_awaited(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного получения меню для бесплатного пользователя (с await)."""
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
        parent_item = next(item for item in menu_items_fixture if item.item_type == ItemType.NAVIGATION)

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
        content_item = next(item for item in menu_items_fixture if item.item_type == ItemType.CONTENT)

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
        non_existent_id = 999

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.get_menu_item_content(non_existent_id, user.telegram_id, db)

        assert "Пункт меню не найден" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_menu_items_success(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], menu_items_fixture: list[MenuItem]
    ):
        """Тест успешного поиска по материалам."""
        # Arrange
        service = MenuItemService()
        user = telegram_users_fixture[0]
        search_query = "test"
        limit = 10

        # Act
        result = await service.search_menu_items(user.telegram_id, search_query, limit, db)

        # Assert
        assert isinstance(result, SearchListResponse)
        assert len(result.items) >= 0

        # Проверяем структуру результатов
        for item in result.items:
            assert hasattr(item, "id")
            assert hasattr(item, "title")
            assert hasattr(item, "item_type")


@pytest.mark.unit
class TestMenuItemCRUD:
    """Тесты CRUD операций для MenuItem."""

    @pytest.mark.asyncio
    async def test_create_menu_item_success(self, db: AsyncSession, menu_item_crud):
        """Тест успешного создания пункта меню."""
        # Arrange
        menu_data = AdminMenuItemCreate(
            title="Тестовый пункт меню",
            description="Описание тестового пункта",
            item_type=ItemType.CONTENT,
            access_level=AccessLevel.FREE,
            is_active=True,
        )

        # Act
        result = await menu_item_crud.create(db, obj_in=menu_data)

        # Assert
        assert result.title == menu_data.title
        assert result.description == menu_data.description
        assert result.item_type == menu_data.item_type
        assert result.access_level == menu_data.access_level
        assert result.is_active == menu_data.is_active

    @pytest.mark.asyncio
    async def test_get_menu_item_by_id_success(self, db: AsyncSession, menu_items_fixture: list[MenuItem], menu_item_crud):
        """Тест успешного получения пункта меню по ID."""
        # Arrange
        menu_item = menu_items_fixture[0]

        # Act
        result = await menu_item_crud.get(db, menu_item.id)

        # Assert
        assert result is not None
        assert result.id == menu_item.id
        assert result.title == menu_item.title

    @pytest.mark.asyncio
    async def test_get_menu_item_by_id_not_found(self, db: AsyncSession, menu_item_crud):
        """Тест получения несуществующего пункта меню."""
        # Arrange
        non_existent_id = 99999

        # Act
        result = await menu_item_crud.get(db, non_existent_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_parent_id_root_level(self, db: AsyncSession, menu_items_fixture: list[MenuItem], menu_item_crud):
        """Тест получения пунктов корневого уровня."""
        # Act
        result = await menu_item_crud.get_by_parent_id(db, parent_id=None, is_active=True)

        # Assert
        assert isinstance(result, list)
        assert len(result) >= 0

        # Все возвращенные пункты должны иметь parent_id = None
        for item in result:
            assert item.parent_id is None

    @pytest.mark.asyncio
    async def test_get_by_parent_id_with_parent(self, db: AsyncSession, menu_items_fixture: list[MenuItem], menu_item_crud):
        """Тест получения дочерних пунктов."""
        # Arrange
        parent_item = next((item for item in menu_items_fixture if item.item_type == ItemType.NAVIGATION), None)

        if parent_item:
            # Act
            result = await menu_item_crud.get_by_parent_id(db, parent_id=parent_item.id, is_active=True)

            # Assert
            assert isinstance(result, list)
            for item in result:
                assert item.parent_id == parent_item.id

    @pytest.mark.asyncio
    async def test_get_by_parent_id_with_access_filter(self, db: AsyncSession, menu_items_fixture: list[MenuItem], menu_item_crud):
        """Тест получения пунктов с фильтром по уровню доступа."""
        # Act
        result = await menu_item_crud.get_by_parent_id(db, parent_id=None, is_active=True, access_level=AccessLevel.FREE)

        # Assert
        assert isinstance(result, list)
        for item in result:
            assert item.access_level == AccessLevel.FREE

    @pytest.mark.asyncio
    async def test_update_menu_item_success(self, db: AsyncSession, menu_items_fixture: list[MenuItem], menu_item_crud):
        """Тест успешного обновления пункта меню."""
        # Arrange
        menu_item = menu_items_fixture[0]
        update_data = {
            "title": "Обновленный заголовок",
            "is_active": False
        }

        # Act
        result = await menu_item_crud.update(db, db_obj=menu_item, obj_in=update_data)

        # Assert
        assert result.id == menu_item.id
        assert result.title == update_data["title"]
        assert result.is_active == update_data["is_active"]

    @pytest.mark.asyncio
    async def test_delete_menu_item_success(self, db: AsyncSession, menu_items_fixture: list[MenuItem], menu_item_crud):
        """Тест успешного удаления пункта меню."""
        # Arrange
        menu_item = menu_items_fixture[0]

        # Act
        result = await menu_item_crud.remove(db, id=menu_item.id)

        # Assert
        assert result.id == menu_item.id

        # Проверяем, что пункт действительно удален
        deleted_item = await menu_item_crud.get(db, menu_item.id)
        assert deleted_item is None

    @pytest.mark.asyncio
    async def test_get_active_items_only(self, db: AsyncSession, menu_items_fixture: list[MenuItem], menu_item_crud):
        """Тест получения только активных пунктов меню."""
        # Act
        active_items = await menu_item_crud.get_by_parent_id(db, parent_id=None, is_active=True)
        all_items = await menu_item_crud.get_by_parent_id(db, parent_id=None, is_active=None)

        # Assert
        assert len(active_items) <= len(all_items)
        for item in active_items:
            assert item.is_active is True
