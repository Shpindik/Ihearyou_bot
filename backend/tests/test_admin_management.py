"""Тесты управления администраторами."""

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.admin_user import AdminUser
from backend.models.enums import AdminRole
from backend.schemas.admin.admin_user import AdminUserCreate, AdminUserListResponse, AdminUserResponse, AdminUserUpdate
from backend.schemas.admin.auth import AdminMeResponse



@pytest.mark.unit
class TestAdminUserAPI:
    """Тесты API эндпоинтов управления администраторами."""

    @pytest.mark.asyncio
    async def test_get_current_admin_info_success(
        self, async_client: AsyncClient, admin_token: str, admin_user: AdminUser
    ):
        """Тест успешного получения информации о текущем администраторе."""
        # Arrange
        endpoint = "/api/v1/admin/auth/me"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_data = {
            "id": admin_user.id,
            "username": admin_user.username,
            "email": admin_user.email,
            "role": admin_user.role
        }

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == expected_data["id"]
        assert data["username"] == expected_data["username"]
        assert data["email"] == expected_data["email"]
        assert data["role"] == expected_data["role"]

    @pytest.mark.asyncio
    async def test_get_current_admin_info_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест получения информации о текущем администраторе без авторизации."""
        # Arrange
        endpoint = "/api/v1/admin/auth/me"
        expected_status_code = 403
        expected_error_message = "Not authenticated"

        # Act
        response = await async_client_no_auth.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
        assert response.json()["error"]["message"] == expected_error_message

    @pytest.mark.asyncio
    async def test_get_current_admin_info_invalid_token(self, async_client_no_auth: AsyncClient):
        """Тест получения информации о текущем администраторе с недействительным токеном."""
        # Arrange
        endpoint = "/api/v1/admin/auth/me"
        headers = {"Authorization": "Bearer invalid_token"}
        expected_status_code = 401

        # Act
        response = await async_client_no_auth.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_admin_users_list_success(self, async_client: AsyncClient, admin_token: str):
        """Тест успешного получения списка администраторов."""
        # Arrange
        endpoint = "/api/v1/admin/users"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 200
        expected_min_items = 1

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= expected_min_items

        # Проверяем структуру первого элемента
        if data["items"]:
            admin = data["items"][0]
            required_fields = ["id", "username", "email", "role", "is_active"]
            for field in required_fields:
                assert field in admin

    @pytest.mark.asyncio
    async def test_get_admin_users_list_moderator_access(self, async_client_moderator: AsyncClient):
        """Тест получения списка администраторов модератором (должен быть запрещен)."""
        # Arrange
        endpoint = "/api/v1/admin/users"
        expected_status_code = 403

        # Act
        response = await async_client_moderator.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_admin_users_list_unauthorized(self, async_client_no_auth: AsyncClient):
        """Тест получения списка администраторов без авторизации."""
        # Arrange
        endpoint = "/api/v1/admin/users"
        expected_status_code = 403
        expected_error_message = "Not authenticated"

        # Act
        response = await async_client_no_auth.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
        assert response.json()["error"]["message"] == expected_error_message

    @pytest.mark.asyncio
    async def test_get_admin_users_list_invalid_token(self, async_client_no_auth: AsyncClient):
        """Тест получения списка администраторов с недействительным токеном."""
        # Arrange
        endpoint = "/api/v1/admin/users"
        headers = {"Authorization": "Bearer invalid_token"}
        expected_status_code = 401

        # Act
        response = await async_client_no_auth.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_create_admin_user_success(self, async_client: AsyncClient, admin_token: str):
        """Тест успешного создания нового администратора."""
        # Arrange
        endpoint = "/api/v1/admin/users"
        headers = {"Authorization": f"Bearer {admin_token}"}
        admin_data = {
            "username": "newadmin",
            "email": "newadmin@example.com",
            "password": "newpassword123",
            "role": "moderator",
        }
        expected_status_code = 201

        # Act
        response = await async_client.post(endpoint, headers=headers, json=admin_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        assert data["username"] == admin_data["username"]
        assert data["email"] == admin_data["email"]
        assert data["role"] == admin_data["role"]
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_admin_user_duplicate_email(
        self, async_client: AsyncClient, admin_token: str, admin_user: AdminUser
    ):
        """Тест создания администратора с уже существующим email."""
        # Arrange
        endpoint = "/api/v1/admin/users"
        headers = {"Authorization": f"Bearer {admin_token}"}
        admin_data = {
            "username": "anotheradmin",
            "email": admin_user.email,  # Уже существует
            "password": "password123",
            "role": "moderator",
        }
        expected_status_code = 400

        # Act
        response = await async_client.post(endpoint, headers=headers, json=admin_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_create_admin_user_invalid_data(self, async_client: AsyncClient, admin_token: str):
        """Тест создания администратора с некорректными данными."""
        # Arrange
        endpoint = "/api/v1/admin/users"
        headers = {"Authorization": f"Bearer {admin_token}"}
        invalid_data = {
            "username": "",  # Пустое имя пользователя
            "email": "invalid-email",
            "password": "123",  # Слишком короткий пароль
            "role": "invalid_role",
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, headers=headers, json=invalid_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_create_admin_user_forbidden_for_moderator(self, async_client_moderator: AsyncClient):
        """Тест создания администратора модератором (должно быть запрещено)."""
        # Arrange
        endpoint = "/api/v1/admin/users"
        admin_data = {
            "username": "newadmin",
            "email": "newadmin@example.com",
            "password": "newpassword123",
            "role": "moderator",
        }
        expected_status_code = 403

        # Act
        response = await async_client_moderator.post(endpoint, json=admin_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_get_admin_user_by_id_success(
        self, async_client: AsyncClient, admin_token: str, admin_user: AdminUser
    ):
        """Тест успешного получения администратора по ID."""
        # Arrange
        endpoint = f"/api/v1/admin/users/{admin_user.id}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 200

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        assert data["id"] == admin_user.id
        assert data["username"] == admin_user.username
        assert data["email"] == admin_user.email

    @pytest.mark.asyncio
    async def test_get_admin_user_by_id_not_found(self, async_client: AsyncClient, admin_token: str):
        """Тест получения несуществующего администратора."""
        # Arrange
        non_existent_id = 99999
        endpoint = f"/api/v1/admin/users/{non_existent_id}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        expected_status_code = 404

        # Act
        response = await async_client.get(endpoint, headers=headers)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_update_admin_user_success(self, async_client: AsyncClient, admin_token: str, admin_user: AdminUser):
        """Тест успешного обновления администратора."""
        # Arrange
        endpoint = f"/api/v1/admin/users/{admin_user.id}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {
            "username": "updatedadmin",
            "email": "updated@example.com",
            "role": "admin",
            "is_active": True
        }
        expected_status_code = 200

        # Act
        response = await async_client.patch(endpoint, headers=headers, json=update_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()

        assert data["username"] == update_data["username"]
        assert data["email"] == update_data["email"]
        assert data["role"] == update_data["role"]

    @pytest.mark.asyncio
    async def test_update_admin_user_forbidden_for_moderator(
        self, async_client_moderator: AsyncClient, admin_user: AdminUser
    ):
        """Тест обновления администратора модератором (должно быть запрещено)."""
        # Arrange
        endpoint = f"/api/v1/admin/users/{admin_user.id}"
        update_data = {"username": "updatedadmin"}
        expected_status_code = 403

        # Act
        response = await async_client_moderator.patch(endpoint, json=update_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_update_admin_password_success(
        self, async_client: AsyncClient, admin_token: str, admin_user: AdminUser
    ):
        """Тест успешного обновления пароля администратора."""
        # Arrange
        endpoint = f"/api/v1/admin/users/{admin_user.id}/password"
        headers = {"Authorization": f"Bearer {admin_token}"}
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        }
        expected_status_code = 200

        # Act
        response = await async_client.patch(endpoint, headers=headers, json=password_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert "id" in data
        assert "username" in data

    @pytest.mark.asyncio
    async def test_update_admin_password_wrong_current(
        self, async_client: AsyncClient, admin_token: str, admin_user: AdminUser
    ):
        """Тест обновления пароля с неправильным текущим паролем."""
        # Arrange
        endpoint = f"/api/v1/admin/users/{admin_user.id}/password"
        headers = {"Authorization": f"Bearer {admin_token}"}
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        }
        expected_status_code = 400

        # Act
        response = await async_client.patch(endpoint, headers=headers, json=password_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_update_admin_password_mismatch(
        self, async_client: AsyncClient, admin_token: str, admin_user: AdminUser
    ):
        """Тест обновления пароля с несовпадающими новым паролем и подтверждением."""
        # Arrange
        endpoint = f"/api/v1/admin/users/{admin_user.id}/password"
        headers = {"Authorization": f"Bearer {admin_token}"}
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "confirm_password": "differentpassword123",  # Не совпадает с new_password
        }
        expected_status_code = 422

        # Act
        response = await async_client.patch(endpoint, headers=headers, json=password_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_deactivate_admin_user_success(self, async_client: AsyncClient, admin_token: str):
        """Тест успешной деактивации администратора."""
        # Arrange - Сначала создадим нового админа для деактивации
        create_endpoint = "/api/v1/admin/users"
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_data = {
            "username": "deactivateme",
            "email": "deactivate@example.com",
            "password": "password123",
            "role": "moderator",
        }

        create_response = await async_client.post(create_endpoint, headers=headers, json=create_data)
        assert create_response.status_code == 201
        new_admin_id = create_response.json()["id"]

        # Act - Деактивируем через обновление
        update_endpoint = f"/api/v1/admin/users/{new_admin_id}"
        update_data = {"is_active": False}
        response = await async_client.patch(update_endpoint, headers=headers, json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    @pytest.mark.asyncio
    async def test_deactivate_admin_user_forbidden_for_moderator(
        self, async_client_moderator: AsyncClient, admin_user: AdminUser
    ):
        """Тест деактивации администратора модератором (должно быть запрещено)."""
        # Arrange
        endpoint = f"/api/v1/admin/users/{admin_user.id}"
        update_data = {"is_active": False}
        expected_status_code = 403

        # Act
        response = await async_client_moderator.patch(endpoint, json=update_data)

        # Assert
        assert response.status_code == expected_status_code


@pytest.mark.unit
class TestAdminUserService:
    """Тесты сервиса AdminUserService."""

    @pytest.mark.asyncio
    async def test_get_current_admin_info_success(self, admin_user_service, admin_user: AdminUser):
        """Тест успешного получения информации о текущем администраторе."""
        # Arrange
        # admin_user предоставляется фикстурой

        # Act
        result = admin_user_service.get_current_admin_info(admin_user)

        # Assert
        assert isinstance(result, AdminMeResponse)
        assert result.id == admin_user.id
        assert result.username == admin_user.username
        assert result.email == admin_user.email

    @pytest.mark.asyncio
    async def test_get_admin_users_for_api_success(self, admin_user_service, db: AsyncSession, mocker):
        """Тест успешного получения списка администраторов."""
        # Arrange
        mock_users = [
            mocker.MagicMock(
                id=1,
                username="admin1",
                email="admin1@example.com",
                role=AdminRole.ADMIN,
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ),
            mocker.MagicMock(
                id=2,
                username="admin2",
                email="admin2@example.com",
                role=AdminRole.MODERATOR,
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ),
        ]

        mocker.patch.object(admin_user_service.admin_crud, "get_all_admins", return_value=mock_users)

        # Act
        result = await admin_user_service.get_admin_users_for_api(db)

        # Assert
        assert isinstance(result, AdminUserListResponse)
        assert len(result.items) == 2
        assert all(isinstance(item, AdminUserResponse) for item in result.items)

    @pytest.mark.asyncio
    async def test_create_admin_for_api_success(self, admin_user_service, db: AsyncSession, mocker):
        """Тест успешного создания администратора."""
        # Arrange
        create_data = AdminUserCreate(
            username="newadmin",
            email="newadmin@example.com",
            password="password123",
            role=AdminRole.MODERATOR
        )

        mock_created_user = mocker.MagicMock(
            id=3,
            username="newadmin",
            email="newadmin@example.com",
            role=AdminRole.MODERATOR,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

        mocker.patch.object(admin_user_service.admin_crud, "create", return_value=mock_created_user)

        # Act
        result = await admin_user_service.create_admin_for_api(db, create_data)

        # Assert
        assert isinstance(result, AdminUserResponse)
        assert result.username == create_data.username
        assert result.email == create_data.email
        assert result.role == create_data.role

    @pytest.mark.asyncio
    async def test_get_admin_user_by_id_success(self, admin_user_service, db: AsyncSession, mocker):
        """Тест успешного получения администратора по ID."""
        # Arrange
        admin_id = 1
        mock_user = mocker.MagicMock(
            id=admin_id,
            username="testadmin",
            email="test@example.com",
            role=AdminRole.ADMIN,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

        mocker.patch.object(admin_user_service.admin_crud, "get", return_value=mock_user)

        # Act
        result = await admin_user_service.get_admin_user_by_id(db, admin_id)

        # Assert
        assert isinstance(result, AdminUserResponse)
        assert result.id == admin_id

    @pytest.mark.asyncio
    async def test_get_admin_user_by_id_not_found(self, admin_user_service, db: AsyncSession, mocker):
        """Тест получения несуществующего администратора."""
        # Arrange
        mocker.patch.object(admin_user_service.admin_crud, "get", return_value=None)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await admin_user_service.get_admin_user_by_id(db, 999)

        assert "не найден" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_admin_for_api_success(self, admin_user_service, db: AsyncSession, mocker):
        """Тест успешного обновления администратора."""
        # Arrange
        admin_id = 1
        update_data = AdminUserUpdate(username="updatedadmin", email="updated@example.com")

        mock_updated_user = mocker.MagicMock(
            id=admin_id,
            username="updatedadmin",
            email="updated@example.com",
            role=AdminRole.ADMIN,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

        mocker.patch.object(admin_user_service, "update_admin_profile", return_value=mock_updated_user)

        # Act
        result = await admin_user_service.update_admin_for_api(db, admin_id, update_data)

        # Assert
        assert isinstance(result, AdminUserResponse)
        assert result.username == "updatedadmin"
        assert result.email == "updated@example.com"


@pytest.mark.unit
class TestAdminUserCRUD:
    """Тесты CRUD операций для AdminUser."""

    @pytest.mark.asyncio
    async def test_create_admin_user_success(self, db: AsyncSession, admin_user_crud, mocker):
        """Тест успешного создания администратора."""
        # Arrange
        user_data = {
            "username": "testadmin",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "role": AdminRole.ADMIN,
            "is_active": True,
        }

        mock_created_user = mocker.MagicMock(**user_data, id=1, created_at=datetime.now(timezone.utc))
        mocker.patch.object(admin_user_crud, "create", return_value=mock_created_user)

        # Act
        result = await admin_user_crud.create(db, obj_in=user_data)

        # Assert
        assert result.username == user_data["username"]
        assert result.email == user_data["email"]
        assert result.role == user_data["role"]

    @pytest.mark.asyncio
    async def test_get_admin_user_by_email_success(
        self, db: AsyncSession, admin_user: AdminUser, admin_user_crud, mocker
    ):
        """Тест успешного получения администратора по email."""
        # Arrange
        email = admin_user.email

        mock_result = mocker.MagicMock()
        mock_result.scalar_one_or_none.return_value = admin_user
        mocker.patch.object(db, "execute", return_value=mock_result)

        # Act
        result = await admin_user_crud.get_by_email(db, email)

        # Assert
        assert result == admin_user

    @pytest.mark.asyncio
    async def test_get_admin_user_by_email_not_found(self, db: AsyncSession, admin_user_crud, mocker):
        """Тест получения администратора по несуществующему email."""
        # Arrange
        mock_result = mocker.MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mocker.patch.object(db, "execute", return_value=mock_result)

        # Act
        result = await admin_user_crud.get_by_email(db, "nonexistent@example.com")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_admin_user_by_username_success(
        self, db: AsyncSession, admin_user: AdminUser, admin_user_crud, mocker
    ):
        """Тест успешного получения администратора по username."""
        # Arrange
        username = admin_user.username

        mock_result = mocker.MagicMock()
        mock_result.scalar_one_or_none.return_value = admin_user
        mocker.patch.object(db, "execute", return_value=mock_result)

        # Act
        result = await admin_user_crud.get_by_username(db, username)

        # Assert
        assert result == admin_user

    @pytest.mark.asyncio
    async def test_update_admin_user_success(self, db: AsyncSession, admin_user_crud, mocker):
        """Тест успешного обновления администратора."""
        # Arrange
        mock_user = mocker.MagicMock(id=1, username="oldname")
        update_data = {"username": "newname"}

        mock_updated_user = mocker.MagicMock(id=1, username="newname")
        mocker.patch.object(admin_user_crud, "update", return_value=mock_updated_user)

        # Act
        result = await admin_user_crud.update(db, db_obj=mock_user, obj_in=update_data)

        # Assert
        assert result.username == "newname"


@pytest.mark.unit
class TestAdminUserValidator:
    """Тесты валидатора AdminUserValidator."""

    def test_validate_admin_active_success(self, admin_user_validator, mocker):
        """Тест успешной валидации активного администратора."""
        # Arrange
        admin_user = mocker.MagicMock(is_active=True, username="testadmin")

        # Act
        result = admin_user_validator.validate_admin_active(admin_user)

        # Assert
        assert result == admin_user

    def test_validate_admin_active_inactive_user(self, admin_user_validator, mocker):
        """Тест валидации неактивного администратора."""
        # Arrange
        admin_user = mocker.MagicMock(is_active=False, username="testadmin")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            admin_user_validator.validate_admin_active(admin_user)

        assert "деактивирован" in str(exc_info.value).lower()

    def test_validate_admin_role_success(self, admin_user_validator, mocker):
        """Тест успешной валидации роли администратора."""
        # Arrange
        admin_user = mocker.MagicMock(role=AdminRole.ADMIN)

        # Act
        result = admin_user_validator.validate_admin_role(admin_user, AdminRole.ADMIN)

        # Assert
        assert result == admin_user

    def test_validate_admin_role_insufficient_permissions(self, admin_user_validator, mocker):
        """Тест валидации роли с недостаточными правами."""
        # Arrange
        admin_user = mocker.MagicMock(role=AdminRole.MODERATOR)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            admin_user_validator.validate_admin_role(admin_user, AdminRole.ADMIN)

        assert "недостаточно прав" in str(exc_info.value).lower()

    def test_validate_admin_roles_success(self, admin_user_validator, mocker):
        """Тест успешной валидации ролей администратора."""
        # Arrange
        admin_user = mocker.MagicMock(role=AdminRole.MODERATOR)

        # Act
        result = admin_user_validator.validate_admin_roles(admin_user, [AdminRole.MODERATOR, AdminRole.ADMIN])

        # Assert
        assert result == admin_user

    def test_validate_admin_roles_insufficient_permissions(self, admin_user_validator, mocker):
        """Тест валидации ролей с недостаточными правами."""
        # Arrange
        admin_user = mocker.MagicMock(role="user")  # Обычный пользователь без прав

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            admin_user_validator.validate_admin_roles(admin_user, [AdminRole.MODERATOR, AdminRole.ADMIN])

        assert "недостаточно прав" in str(exc_info.value).lower()

    def test_validate_email_unique_success(self, admin_user_validator):
        """Тест успешной валидации уникальности email."""
        # Arrange
        existing_admin = None  # Email уникален

        # Act & Assert - не должно быть исключения
        admin_user_validator.validate_email_unique(existing_admin)

    def test_validate_email_unique_duplicate(self, admin_user_validator, mocker):
        """Тест валидации неуникального email."""
        # Arrange
        existing_admin = mocker.MagicMock(id=1, email="duplicate@example.com")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            admin_user_validator.validate_email_unique(existing_admin)

        assert "уже существует" in str(exc_info.value).lower()

    def test_validate_login_format_email(self, admin_user_validator):
        """Тест валидации формата логина (email)."""
        # Arrange
        valid_email = "test@example.com"

        # Act & Assert - не должно быть исключения
        admin_user_validator.validate_login_format(valid_email)

    def test_validate_login_format_username(self, admin_user_validator):
        """Тест валидации формата логина (username)."""
        # Arrange
        valid_username = "testuser"

        # Act & Assert - не должно быть исключения
        admin_user_validator.validate_login_format(valid_username)
