"""Тесты базовой инфраструктуры."""

import pytest
from fastapi import HTTPException, status

from backend.core.config import Settings
from backend.core.db import Base, engine, get_session
from backend.core.dependencies import get_current_admin, require_admin_role, require_moderator_or_admin_role
from backend.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_password_reset_token,
    verify_token,
    verify_token_payload_for_password_reset,
)
from backend.validators.admin_user import admin_user_validator
from backend.models.admin_user import AdminUser
from backend.models.enums import AdminRole
from backend.tests.test_config import test_settings


@pytest.mark.unit
class TestSettings:
    """Тесты конфигурации приложения."""

    def test_settings_creation_with_env_vars(self, monkeypatch):
        """Тест создания настроек с переменными окружения."""
        # Arrange
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/testdb")
        monkeypatch.setenv("JWT_SECRET_KEY", "test_secret_key")
        monkeypatch.setenv("MAIL_USERNAME", "test@example.com")

        # Act
        settings = Settings()

        # Assert
        assert settings.database_url == "postgresql+asyncpg://test:test@localhost/testdb"
        assert settings.jwt_secret_key == "test_secret_key"
        assert settings.mail_username == "test@example.com"

    def test_settings_default_values(self):
        """Тест значений по умолчанию."""
        # Arrange
        expected_values = {
            "jwt_algorithm": "HS256",
            "jwt_access_token_expire_minutes": 60,
            "jwt_refresh_token_expire_days": 7,
            "bot_api_port": 8001,
            "frontend_port": 3001,
            "environment": "development",
            "debug": False
        }

        # Act
        settings = Settings()

        # Assert
        assert settings.jwt_algorithm == expected_values["jwt_algorithm"]
        assert settings.jwt_access_token_expire_minutes == expected_values["jwt_access_token_expire_minutes"]
        assert settings.jwt_refresh_token_expire_days == expected_values["jwt_refresh_token_expire_days"]
        assert settings.bot_api_port == expected_values["bot_api_port"]
        assert settings.frontend_port == expected_values["frontend_port"]
        assert settings.environment == expected_values["environment"]
        assert settings.debug == expected_values["debug"]

    def test_email_conf_creation(self):
        """Тест создания конфигурации email."""
        # Arrange
        settings = Settings()
        settings.mail_username = "test@example.com"
        settings.mail_password = "password"
        settings.mail_server = "smtp.gmail.com"
        settings.mail_port = 587

        expected_config = {
            "MAIL_USERNAME": "test@example.com",
            "MAIL_PASSWORD": "password",
            "MAIL_SERVER": "smtp.gmail.com",
            "MAIL_PORT": 587,
            "MAIL_STARTTLS": True,
            "MAIL_SSL_TLS": False
        }

        # Act
        email_conf = settings.email_conf()

        # Assert
        assert email_conf.MAIL_USERNAME == expected_config["MAIL_USERNAME"]
        assert email_conf.MAIL_PASSWORD == expected_config["MAIL_PASSWORD"]
        assert email_conf.MAIL_SERVER == expected_config["MAIL_SERVER"]
        assert email_conf.MAIL_PORT == expected_config["MAIL_PORT"]
        assert email_conf.MAIL_STARTTLS == expected_config["MAIL_STARTTLS"]
        assert email_conf.MAIL_SSL_TLS == expected_config["MAIL_SSL_TLS"]


@pytest.mark.unit
class TestSecurityFunctions:
    """Тесты функций безопасности и JWT."""

    @pytest.mark.parametrize(
        "plain_password,input_password,expected_result",
        [
            ("testpassword", "testpassword", True),  # Корректный пароль
            ("testpassword", "wrongpassword", False),  # Неправильный пароль
        ],
    )
    def test_verify_password(self, mocker, plain_password, input_password, expected_result):
        """Тест проверки пароля."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        hashed_password = get_password_hash(plain_password)

        # Act
        result = verify_password(input_password, hashed_password)

        # Assert
        assert result is expected_result

    def test_get_password_hash(self):
        """Тест хеширования пароля."""
        # Arrange
        password = "testpassword"
        expected_prefix = "$pbkdf2-sha256$"

        # Act
        hashed = get_password_hash(password)

        # Assert
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith(expected_prefix)

    def test_create_access_token(self, mocker):
        """Тест создания access токена."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        data = {"sub": "testuser", "role": "admin"}
        expected_fields = ["sub", "role", "exp"]

        # Act
        token = create_access_token(data)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0

        # Проверяем декодирование
        payload = verify_token(token)
        assert payload["sub"] == data["sub"]
        assert payload["role"] == data["role"]
        for field in expected_fields:
            assert field in payload

    def test_create_refresh_token(self, mocker):
        """Тест создания refresh токена."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        data = {"sub": "testuser"}

        # Act
        token = create_refresh_token(data)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self, mocker):
        """Тест проверки валидного токена."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)

        # Act
        payload = verify_token(token)

        # Assert
        assert payload["sub"] == data["sub"]
        assert payload["role"] == data["role"]

    def test_verify_token_invalid(self, mocker):
        """Тест проверки невалидного токена."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        invalid_token = "invalid_token"
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        expected_error_message = "Недействительный токен"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)
        
        assert exc_info.value.status_code == expected_status_code
        assert expected_error_message in exc_info.value.detail

    def test_create_password_reset_token(self, mocker):
        """Тест создания токена восстановления пароля."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        email = "test@example.com"

        # Act
        token = create_password_reset_token(email)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_password_reset_token_valid(self, mocker):
        """Тест проверки валидного токена восстановления пароля."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        email = "test@example.com"
        token = create_password_reset_token(email)

        # Act
        result = verify_password_reset_token(token)

        # Assert
        assert result == email

    def test_verify_password_reset_token_invalid(self, mocker):
        """Тест проверки невалидного токена восстановления пароля."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        invalid_token = "invalid_token"

        # Act
        result = verify_password_reset_token(invalid_token)

        # Assert
        assert result is None

    def test_verify_token_payload_for_password_reset_valid(self, mocker):
        """Тест валидации payload токена восстановления пароля."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        email = "test@example.com"
        token = create_password_reset_token(email)
        payload = verify_token(token)

        # Act
        result = verify_token_payload_for_password_reset(payload)

        # Assert
        assert result == email

    def test_verify_token_payload_for_password_reset_invalid_type(self, mocker):
        """Тест валидации payload с неправильным типом токена."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        payload = {"email": "test@example.com", "type": "access"}
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        expected_error_message = "Недействительный токен восстановления"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            verify_token_payload_for_password_reset(payload)
        
        assert exc_info.value.status_code == expected_status_code
        assert expected_error_message in exc_info.value.detail

    def test_verify_token_payload_for_password_reset_no_email(self, mocker):
        """Тест валидации payload без email."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        payload = {"type": "password_reset"}
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        expected_error_message = "Отсутствует email в токене"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            verify_token_payload_for_password_reset(payload)
        
        assert exc_info.value.status_code == expected_status_code
        assert expected_error_message in exc_info.value.detail


@pytest.mark.unit
class TestDatabaseConnection:
    """Тесты подключения к базе данных."""

    @pytest.mark.asyncio
    async def test_get_session_creation(self):
        """Тест создания сессии базы данных."""
        # Act
        session_generator = get_session()

        # Assert
        assert hasattr(session_generator, "__aiter__") or hasattr(session_generator, "__anext__")

    def test_engine_creation(self):
        """Тест создания движка базы данных."""
        # Assert
        assert engine is not None
        assert hasattr(engine, "connect")

    def test_base_class_creation(self):
        """Тест создания базового класса для моделей."""
        # Assert
        assert Base is not None
        assert hasattr(Base, "metadata")
        assert hasattr(Base.metadata, "tables")


@pytest.mark.unit
class TestDependencies:
    """Тесты зависимостей FastAPI."""

    @pytest.mark.asyncio
    async def test_get_current_admin_success(self, mocker, admin_user):
        """Тест успешного получения текущего администратора."""
        # Arrange
        mock_credentials = mocker.MagicMock()
        mock_credentials.credentials = "valid_token"
        mock_session = mocker.MagicMock()
        
        mock_service = mocker.patch("backend.core.dependencies.admin_user_service")
        mock_service.authenticate_admin_by_token = mocker.AsyncMock(return_value=admin_user)

        # Act
        result = await get_current_admin(mock_credentials, mock_session)

        # Assert
        assert result == admin_user
        mock_service.authenticate_admin_by_token.assert_called_once_with(mock_session, "valid_token")

    def test_require_admin_role_success(self, mocker, admin_user):
        """Тест успешного требования роли администратора."""
        # Arrange
        mock_validator = mocker.patch("backend.core.dependencies.admin_user_validator")
        mock_validator.validate_admin_role.return_value = admin_user

        # Act
        result = require_admin_role(admin_user)

        # Assert
        assert result == admin_user
        mock_validator.validate_admin_role.assert_called_once_with(admin_user, AdminRole.ADMIN)

    def test_require_moderator_or_admin_role_success(self, mocker, moderator_user):
        """Тест успешного требования роли модератора или администратора."""
        # Arrange
        mock_validator = mocker.patch("backend.core.dependencies.admin_user_validator")
        mock_validator.validate_admin_roles.return_value = moderator_user

        # Act
        result = require_moderator_or_admin_role(moderator_user)

        # Assert
        assert result == moderator_user
        mock_validator.validate_admin_roles.assert_called_once()


@pytest.mark.unit
class TestAdminUserValidator:
    """Тесты валидатора административных пользователей."""

    def test_validate_token_payload_valid(self):
        """Тест валидации валидного payload токена."""
        # Arrange
        payload = {"sub": "123", "role": "admin"}
        expected_user_id = "123"

        # Act
        result = admin_user_validator.validate_token_payload(payload)

        # Assert
        assert result == expected_user_id

    def test_validate_token_payload_invalid_missing_sub(self):
        """Тест валидации payload токена без поля sub."""
        # Arrange
        payload = {"role": "admin"}  # Нет поля 'sub'
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        expected_error_message = "Недействительный токен"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            admin_user_validator.validate_token_payload(payload)
        
        assert exc_info.value.status_code == expected_status_code
        assert expected_error_message in exc_info.value.detail

    def test_validate_token_payload_invalid_empty_sub(self):
        """Тест валидации payload токена с пустым полем sub."""
        # Arrange
        payload = {"sub": None, "role": "admin"}
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        expected_error_message = "Недействительный токен"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            admin_user_validator.validate_token_payload(payload)
        
        assert exc_info.value.status_code == expected_status_code
        assert expected_error_message in exc_info.value.detail

    def test_validate_admin_role_success(self, admin_user):
        """Тест успешной валидации роли администратора."""
        # Act
        result = admin_user_validator.validate_admin_role(admin_user, AdminRole.ADMIN)

        # Assert
        assert result == admin_user

    def test_validate_admin_role_forbidden(self, moderator_user):
        """Тест валидации роли администратора с недостаточными правами."""
        # Arrange
        expected_status_code = status.HTTP_403_FORBIDDEN
        expected_error_message = "Недостаточно прав"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            admin_user_validator.validate_admin_role(moderator_user, AdminRole.ADMIN)

        assert exc_info.value.status_code == expected_status_code
        assert expected_error_message in str(exc_info.value.detail)

    def test_validate_admin_roles_success(self, moderator_user):
        """Тест успешной валидации ролей администратора."""
        # Arrange
        allowed_roles = [AdminRole.MODERATOR, AdminRole.ADMIN]

        # Act
        result = admin_user_validator.validate_admin_roles(moderator_user, allowed_roles)

        # Assert
        assert result == moderator_user

    def test_validate_admin_roles_forbidden(self, moderator_user):
        """Тест валидации ролей администратора с недостаточными правами."""
        # Arrange
        allowed_roles = [AdminRole.ADMIN]
        expected_status_code = status.HTTP_403_FORBIDDEN
        expected_error_message = "Недостаточно прав"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            admin_user_validator.validate_admin_roles(moderator_user, allowed_roles)

        assert exc_info.value.status_code == expected_status_code
        assert expected_error_message in str(exc_info.value.detail)

    def test_validate_admin_exists_success(self):
        """Тест успешной валидации существования администратора."""
        # Arrange
        admin_user = AdminUser(
            id=1,
            username="testadmin",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True,
            role=AdminRole.ADMIN
        )

        # Act
        result = admin_user_validator.validate_admin_exists(admin_user)

        # Assert
        assert result == admin_user

    def test_validate_admin_exists_not_found(self):
        """Тест валидации несуществующего администратора."""
        # Arrange
        expected_status_code = status.HTTP_404_NOT_FOUND
        expected_error_message = "Администратор не найден"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            admin_user_validator.validate_admin_exists(None)

        assert exc_info.value.status_code == expected_status_code
        assert expected_error_message in str(exc_info.value.detail)

    def test_validate_admin_active_success(self, admin_user):
        """Тест успешной валидации активного администратора."""
        # Act
        result = admin_user_validator.validate_admin_active(admin_user)

        # Assert
        assert result == admin_user

    def test_validate_admin_active_unauthorized(self, admin_user):
        """Тест валидации неактивного администратора."""
        # Arrange
        admin_user.is_active = False
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        expected_error_message = "Пользователь деактивирован"
        expected_headers = {"WWW-Authenticate": "Bearer"}

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            admin_user_validator.validate_admin_active(admin_user)

        assert exc_info.value.status_code == expected_status_code
        assert expected_error_message in str(exc_info.value.detail)
        assert exc_info.value.headers == expected_headers

    def test_validate_token_payload_edge_cases(self):
        """Тест валидации payload токена с граничными случаями."""
        # Arrange
        test_cases = [
            ({}, "Недействительный токен"),
            ({"sub": None}, "Недействительный токен"),
        ]
        expected_status_code = status.HTTP_401_UNAUTHORIZED

        # Act & Assert
        for payload, expected_error in test_cases:
            with pytest.raises(HTTPException) as exc_info:
                admin_user_validator.validate_token_payload(payload)
            assert exc_info.value.status_code == expected_status_code
            assert expected_error in exc_info.value.detail

        # Тест с пустой строкой в sub - этот случай должен пройти валидацию
        result = admin_user_validator.validate_token_payload({"sub": ""})
        assert result == ""

    def test_validate_admin_role_edge_cases(self, admin_user):
        """Тест валидации роли администратора с граничными случаями."""
        # Arrange
        admin_user.role = None
        expected_status_code = status.HTTP_403_FORBIDDEN

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            admin_user_validator.validate_admin_role(admin_user, AdminRole.ADMIN)
        
        assert exc_info.value.status_code == expected_status_code

    def test_validate_admin_roles_edge_cases(self, admin_user):
        """Тест валидации ролей администратора с граничными случаями."""
        # Arrange
        test_cases = [
            ([], status.HTTP_403_FORBIDDEN),  # Пустой список ролей
        ]
        
        # Тест с пустым списком ролей
        with pytest.raises(HTTPException) as exc_info:
            admin_user_validator.validate_admin_roles(admin_user, [])
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

        # Тест с None ролью
        admin_user.role = None
        with pytest.raises(HTTPException) as exc_info:
            admin_user_validator.validate_admin_roles(admin_user, [AdminRole.ADMIN])
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.unit
class TestSecurityFunctionsEdgeCases:
    """Тесты функций безопасности с граничными случаями."""

    def test_verify_token_edge_cases(self, mocker):
        """Тест проверки токена с граничными случаями."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        test_cases = [
            ("", "Недействительный токен"),
            ("not.a.jwt.token", "Недействительный токен"),
        ]
        expected_status_code = status.HTTP_401_UNAUTHORIZED

        # Act & Assert
        for invalid_token, expected_error in test_cases:
            with pytest.raises(HTTPException) as exc_info:
                verify_token(invalid_token)
            assert exc_info.value.status_code == expected_status_code
            assert expected_error in exc_info.value.detail

    def test_verify_password_edge_cases(self):
        """Тест проверки пароля с граничными случаями."""
        # Arrange
        test_cases = [
            ("", True),  # Пустой пароль
            ("a" * 1000, True),  # Очень длинный пароль
        ]

        # Act & Assert
        for password, expected_result in test_cases:
            hashed_password = get_password_hash(password)
            result = verify_password(password, hashed_password)
            assert result is expected_result

    def test_create_access_token_edge_cases(self, mocker):
        """Тест создания access токена с граничными случаями."""
        # Arrange
        mocker.patch("backend.core.security.settings", test_settings)
        test_cases = [
            ({}, True),  # Пустой data
            ({"sub": None}, True),  # None в data
        ]

        # Act & Assert
        for data, should_succeed in test_cases:
            token = create_access_token(data)
            assert isinstance(token, str)
            assert len(token) > 0
