"""Тесты системы уведомлений."""

import pytest
from httpx import AsyncClient


@pytest.mark.unit
class TestNotificationsAPI:
    """Тесты API эндпоинтов системы уведомлений."""

    @pytest.mark.asyncio
    async def test_get_notifications_success(self, async_client: AsyncClient, admin_token: str):
        """Тест успешного получения списка уведомлений."""
        # Arrange
        endpoint = "/api/v1/admin/notifications"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 200

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_notifications_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест получения уведомлений без авторизации."""
        # Arrange
        endpoint = "/api/v1/admin/notifications"
        expected_status_code = 403

        # Act
        response = await async_client_no_auth.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_notifications_invalid_token(self, async_client_no_auth: AsyncClient):
        """Тест получения уведомлений с недействительным токеном."""
        # Arrange
        endpoint = "/api/v1/admin/notifications"
        headers = {"Authorization": "Bearer invalid_token"}
        expected_status_code = 401

        # Act
        response = await async_client_no_auth.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_create_notification_success(self, async_client: AsyncClient, admin_token: str, telegram_users_fixture):
        """Тест успешного создания уведомления."""
        # Arrange
        endpoint = "/api/v1/admin/notifications"
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Используем существующего пользователя из фикстуры
        test_user = telegram_users_fixture[0]
        notification_data = {
            "telegram_user_id": test_user.telegram_id,
            "message": "This is a test notification message with sufficient length"
        }
        expected_status_code = 201

        # Act
        response = await async_client.post(endpoint, headers=headers, json=notification_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_create_notification_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест создания уведомления без авторизации."""
        # Arrange
        endpoint = "/api/v1/admin/notifications"
        notification_data = {
            "title": "Test Notification",
            "message": "This is a test notification"
        }
        expected_status_code = 403

        # Act
        response = await async_client_no_auth.post(endpoint, json=notification_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_create_notification_invalid_data(self, async_client: AsyncClient, admin_token: str, telegram_users_fixture):
        """Тест создания уведомления с некорректными данными."""
        # Arrange
        endpoint = "/api/v1/admin/notifications"
        headers = {"Authorization": f"Bearer {admin_token}"}
        test_user = telegram_users_fixture[0]
        invalid_data = {
            "telegram_user_id": test_user.telegram_id,
            "message": "short"  # Слишком короткое сообщение (меньше 10 символов)
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, headers=headers, json=invalid_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_update_notification_success(self, async_client: AsyncClient, admin_token: str, telegram_users_fixture):
        """Тест успешного обновления уведомления."""
        # Arrange - сначала создаем уведомление
        create_endpoint = "/api/v1/admin/notifications"
        headers = {"Authorization": f"Bearer {admin_token}"}
        test_user = telegram_users_fixture[0]
        notification_data = {
            "telegram_user_id": test_user.telegram_id,
            "message": "Test notification for update"
        }
        
        # Создаем уведомление
        create_response = await async_client.post(create_endpoint, headers=headers, json=notification_data)
        assert create_response.status_code == 201
        created_notification = create_response.json()
        notification_id = created_notification["id"]
        
        # Теперь обновляем его
        update_endpoint = f"/api/v1/admin/notifications/{notification_id}"
        update_data = {
            "status": "sent"
        }
        expected_status_code = 200

        # Act
        response = await async_client.patch(update_endpoint, headers=headers, json=update_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_update_notification_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест обновления уведомления без авторизации."""
        # Arrange
        notification_id = 1
        endpoint = f"/api/v1/admin/notifications/{notification_id}"
        update_data = {"is_active": False}
        expected_status_code = 403

        # Act
        response = await async_client_no_auth.patch(endpoint, json=update_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_update_notification_not_found(self, async_client: AsyncClient, admin_token: str):
        """Тест обновления несуществующего уведомления."""
        # Arrange
        non_existent_id = 99999
        endpoint = f"/api/v1/admin/notifications/{non_existent_id}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {"status": "sent"}
        expected_status_code = 404

        # Act
        response = await async_client.patch(endpoint, headers=headers, json=update_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_delete_notification_success(self, async_client: AsyncClient, admin_token: str, telegram_users_fixture):
        """Тест успешного удаления уведомления."""
        # Arrange - сначала создаем уведомление
        create_endpoint = "/api/v1/admin/notifications"
        headers = {"Authorization": f"Bearer {admin_token}"}
        test_user = telegram_users_fixture[0]
        notification_data = {
            "telegram_user_id": test_user.telegram_id,
            "message": "Test notification for deletion"
        }
        
        # Создаем уведомление
        create_response = await async_client.post(create_endpoint, headers=headers, json=notification_data)
        assert create_response.status_code == 201
        created_notification = create_response.json()
        notification_id = created_notification["id"]
        
        # Теперь удаляем его
        delete_endpoint = f"/api/v1/admin/notifications/{notification_id}"
        expected_status_code = 204

        # Act
        response = await async_client.delete(delete_endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_delete_notification_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест удаления уведомления без авторизации."""
        # Arrange
        notification_id = 1
        endpoint = f"/api/v1/admin/notifications/{notification_id}"
        expected_status_code = 403

        # Act
        response = await async_client_no_auth.delete(endpoint)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_delete_notification_not_found(self, async_client: AsyncClient, admin_token: str):
        """Тест удаления несуществующего уведомления."""
        # Arrange
        non_existent_id = 99999
        endpoint = f"/api/v1/admin/notifications/{non_existent_id}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 404

        # Act
        response = await async_client.delete(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_mark_notification_as_read_endpoint_not_found(self, async_client: AsyncClient, admin_token: str):
        """Тест отметки уведомления как прочитанного - эндпоинт не существует."""
        # Arrange
        notification_id = 1
        endpoint = f"/api/v1/admin/notifications/{notification_id}/read"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 404

        # Act
        response = await async_client.patch(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_mark_notification_as_read_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест отметки уведомления как прочитанного без авторизации - эндпоинт не существует."""
        # Arrange
        notification_id = 1
        endpoint = f"/api/v1/admin/notifications/{notification_id}/read"
        expected_status_code = 404

        # Act
        response = await async_client_no_auth.patch(endpoint)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_notification_statistics_success(self, async_client: AsyncClient, admin_token: str):
        """Тест успешного получения статистики уведомлений."""
        # Arrange
        endpoint = "/api/v1/admin/notifications/statistics"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 200

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_notification_statistics_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест получения статистики уведомлений без авторизации."""
        # Arrange
        endpoint = "/api/v1/admin/notifications/statistics"
        expected_status_code = 403

        # Act
        response = await async_client_no_auth.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
