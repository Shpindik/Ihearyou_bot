"""Тесты API шаблонов сообщений."""

import pytest


@pytest.mark.unit
class TestAdminMessageTemplateAPI:
    """Тесты API эндпоинтов администрирования шаблонов сообщений."""

    @pytest.mark.asyncio
    async def test_get_all_templates_success(self, admin_client, inactive_template, active_template):
        """Тест успешного получения списка всех шаблонов сообщений."""
        # Arrange
        endpoint = "/api/v1/admin/message-templates/"
        expected_status_code = 200
        expected_items_count = 2
        expected_keys = {"id", "name", "message_template", "is_active", "created_at", "updated_at"}

        # Act
        response = await admin_client.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
        response_data = response.json()
        
        assert "items" in response_data
        items = response_data["items"]
        assert isinstance(items, list)
        assert len(items) == expected_items_count

        # Проверяем структуру первого элемента
        first_item = items[0]
        missing_keys = expected_keys - first_item.keys()
        assert not missing_keys, f"Отсутствуют ключи: {missing_keys}"

        # Проверяем, что возвращены ожидаемые шаблоны
        item_ids = {item["id"] for item in items}
        expected_ids = {inactive_template.id, active_template.id}
        assert item_ids == expected_ids

    @pytest.mark.parametrize(
        "template_data,expected_active",
        [
            (
                {
                    "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас.",
                    "name": "Active template"
                },
                True
            ),
            (
                {
                    "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас",
                    "name": "Inactive template",
                    "is_active": False
                },
                False
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_template_success(self, admin_client, template_data, expected_active):
        """Тест успешного создания шаблона сообщения."""
        # Arrange
        endpoint = "/api/v1/admin/message-templates/"
        expected_status_code = 201
        expected_keys = {"id", "name", "message_template", "is_active", "created_at", "updated_at"}

        # Act
        response = await admin_client.post(endpoint, json=template_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        missing_keys = expected_keys - data.keys()
        assert not missing_keys, f"Отсутствуют ключи: {missing_keys}"

        assert data["name"] == template_data["name"]
        assert data["message_template"] == template_data["message_template"]
        assert data["is_active"] == expected_active

    @pytest.mark.parametrize(
        "invalid_data",
        [
            {"name": "", "message_template": "empty name"},  # Пустое имя
            {"name": 10, "message_template": "integer name"},  # Целое число вместо строки
            {"name": "ab", "message_template": "short name"},  # Слишком короткое имя
            {"name": None, "message_template": "null name"},  # None вместо строки
            {"name": "integer message", "message_template": 10},  # Целое число вместо сообщения
            {"name": "null message", "message_template": None},  # None вместо сообщения
            {"name": "too_long" * 32, "message_template": "too long name"},  # Слишком длинное имя
            {"name": "too_long_message", "message_template": "a" * 4001},  # Слишком длинное сообщение
            {"name": "Wrong is_active", "message_template": "We miss you", "is_active": "active"},  # Строка вместо bool
            {"name": "Wrong is_active", "message_template": "We miss you", "is_active": None},  # None вместо bool
            {"name": "Wrong is_active", "message_template": "We miss you", "is_active": 2},  # Число вместо bool
        ],
    )
    @pytest.mark.asyncio
    async def test_create_template_invalid_data(self, admin_client, invalid_data):
        """Тест создания шаблона с некорректными данными."""
        # Arrange
        endpoint = "/api/v1/admin/message-templates/"
        expected_status_code = 422

        # Act
        response = await admin_client.post(endpoint, json=invalid_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_create_template_unauthorized(self, async_client_no_auth):
        """Тест создания шаблона без авторизации."""
        # Arrange
        endpoint = "/api/v1/admin/message-templates/"
        template_data = {
            "name": "test_name",
            "message_template": "We miss you very much and hope to see you again soon!"
        }
        expected_status_code = 403

        # Act
        response = await async_client_no_auth.post(endpoint, json=template_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "update_data,expected_name,expected_message,expected_active",
        [
            ({}, "Active template", "Hello, {first_name}! Message for active template", True),  # Пустое обновление
            (
                {"name": "Other_name", "message_template": "Other_message template message", "is_active": False},
                "Other_name",
                "Other_message template message",
                False
            ),  # Полное обновление
        ],
    )
    @pytest.mark.asyncio
    async def test_update_template_success(
        self, admin_client, active_template, update_data, expected_name, expected_message, expected_active
    ):
        """Тест успешного обновления шаблона сообщения."""
        # Arrange
        endpoint = f"/api/v1/admin/message-templates/{active_template.id}"
        expected_status_code = 200
        expected_keys = {"id", "name", "message_template", "is_active", "created_at", "updated_at"}

        # Act
        response = await admin_client.patch(endpoint, json=update_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        missing_keys = expected_keys - data.keys()
        assert not missing_keys, f"Отсутствуют ключи: {missing_keys}"

        assert data["id"] == active_template.id
        assert data["name"] == expected_name
        assert data["message_template"] == expected_message
        assert data["is_active"] == expected_active

    @pytest.mark.asyncio
    async def test_update_template_unauthorized(self, async_client_no_auth, active_template):
        """Тест обновления шаблона без авторизации."""
        # Arrange
        endpoint = f"/api/v1/admin/message-templates/{active_template.id}"
        update_data = {
            "name": "Other_name",
            "message_template": "Other message template that is long enough for validation",
            "is_active": False
        }
        expected_status_code = 403

        # Act
        response = await async_client_no_auth.patch(endpoint, json=update_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "invalid_data",
        [
            {"name": ""},  # Пустое имя
            {"name": 100},  # Целое число
            {"name": "aa"},  # Слишком короткое имя
            {"message_template": ""},  # Пустое сообщение
            {"message_template": 5},  # Целое число
            {"message_template": "a" * 19},  # Слишком короткое сообщение
            {"message_template": "a" * 4001},  # Слишком длинное сообщение
            {"name": "too_long" * 32},  # Слишком длинное имя
            {"is_active": "active"},  # Строка вместо bool
            {"is_active": 2},  # Число вместо bool
        ],
    )
    @pytest.mark.asyncio
    async def test_update_template_invalid_data(self, admin_client, active_template, invalid_data):
        """Тест обновления шаблона с некорректными данными."""
        # Arrange
        endpoint = f"/api/v1/admin/message-templates/{active_template.id}"
        expected_status_code = 422

        # Act
        response = await admin_client.patch(endpoint, json=invalid_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_delete_template_success(self, admin_client, active_template):
        """Тест успешного удаления шаблона сообщения."""
        # Arrange
        list_endpoint = "/api/v1/admin/message-templates/"
        delete_endpoint = f"/api/v1/admin/message-templates/{active_template.id}"
        expected_status_code = 204

        # Получаем количество шаблонов до удаления
        response_before = await admin_client.get(list_endpoint)
        objects_before = len(response_before.json()["items"])

        # Act
        response = await admin_client.delete(delete_endpoint)

        # Assert
        assert response.status_code == expected_status_code

        # Проверяем, что шаблон действительно удален
        response_after = await admin_client.get(list_endpoint)
        objects_after = len(response_after.json()["items"])
        assert objects_after == objects_before - 1

    @pytest.mark.asyncio
    async def test_delete_template_unauthorized(self, async_client_no_auth, active_template):
        """Тест удаления шаблона без авторизации."""
        # Arrange
        endpoint = f"/api/v1/admin/message-templates/{active_template.id}"
        expected_status_code = 403

        # Act
        response = await async_client_no_auth.delete(endpoint)

        # Assert
        assert response.status_code == expected_status_code


@pytest.mark.unit
class TestBotMessageTemplateAPI:
    """Тесты Bot API для шаблонов сообщений."""

    @pytest.mark.asyncio
    async def test_get_active_template_success(self, async_client, active_template):
        """Тест успешного получения активного шаблона сообщения."""
        # Arrange
        endpoint = "/api/v1/bot/message-template/active-template"
        expected_status_code = 200
        expected_keys = {"id", "name", "message_template", "created_at"}

        # Act
        response = await async_client.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
        response_data = response.json()

        missing_keys = expected_keys - response_data.keys()
        assert not missing_keys, f"Отсутствуют ключи: {missing_keys}"

        assert response_data["id"] == active_template.id
        assert response_data["name"] == active_template.name
        assert "{first_name}" in response_data["message_template"]

    @pytest.mark.asyncio
    async def test_get_active_template_when_no_active(self, async_client):
        """Тест получения активного шаблона когда активных шаблонов нет."""
        # Arrange
        endpoint = "/api/v1/bot/message-template/active-template"
        expected_status_code = 200
        expected_keys = {"id", "name", "message_template", "created_at"}

        # Act
        response = await async_client.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
        response_data = response.json()

        missing_keys = expected_keys - response_data.keys()
        assert not missing_keys, f"Отсутствуют ключи: {missing_keys}"

        assert "{first_name}" in response_data["message_template"]
