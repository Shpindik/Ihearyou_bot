"""Валидатор для работы с административными пользователями."""

from __future__ import annotations

from typing import Optional

from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException, status

from backend.core.config import settings
from backend.core.exceptions import AuthenticationError
from backend.models.admin_user import AdminUser
from backend.models.enums import AdminRole


class AdminUserValidator:
    """Валидатор для работы с административными пользователями."""

    def __init__(self):
        """Инициализация валидатора Admin User."""

    def validate_admin_exists(self, admin: Optional[AdminUser]) -> AdminUser:
        """Валидация существования администратора в базе данных.

        Args:
            admin: Объект администратора (результат поиска в БД)

        Returns:
            AdminUser: Подтвержденного существующего администратора

        Raises:
            HTTPException: 404 если администратор не найден в БД
        """
        if not isinstance(admin, AdminUser):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден")
        return admin

    def validate_admin_active(self, admin: AdminUser) -> AdminUser:
        """Валидация активности администратора.

        Args:
            admin: Администратор для проверки

        Returns:
            AdminUser: Активный администратор

        Raises:
            HTTPException: 401 если администратор неактивен
        """
        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь деактивирован",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return admin

    def validate_admin_role(self, admin: AdminUser, required_role: AdminRole) -> AdminUser:
        """Валидация роли администратора.

        Args:
            admin: Администратор для проверки
            required_role: Требуемая роль

        Returns:
            AdminUser: Администратор с требуемой ролью

        Raises:
            HTTPException: 403 если недостаточно прав
        """
        if admin.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Недостаточно прав. Требуется роль {required_role.value}"
            )
        return admin

    def validate_admin_roles(self, admin: AdminUser, allowed_roles: list[AdminRole]) -> AdminUser:
        """Валидация ролей администратора (одна из разрешенных).

        Args:
            admin: Администратор для проверки
            allowed_roles: Список разрешенных ролей

        Returns:
            AdminUser: Администратор с разрешенной ролью

        Raises:
            HTTPException: 403 если недостаточно прав
        """
        if admin.role not in allowed_roles:
            roles_str = ", ".join([role.value for role in allowed_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Недостаточно прав. Требуется одна из ролей: {roles_str}"
            )
        return admin

    def validate_username_unique(self, existing_admin: Optional[AdminUser], exclude_id: Optional[int] = None) -> None:
        """Валидация уникальности имени пользователя.

        Args:
            existing_admin: Существующий администратор (уже полученный из БД)
            exclude_id: ID администратора для исключения из проверки (при обновлении)

        Raises:
            HTTPException: 400 если имя пользователя уже существует
        """
        if existing_admin and (exclude_id is None or existing_admin.id != exclude_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким именем уже существует"
            )

    def validate_password_strength(self, password: str) -> None:
        """Валидация силы пароля.

        Args:
            password: Пароль для проверки

        Raises:
            HTTPException: 400 если пароль не соответствует требованиям
        """
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пароль должен содержать минимум 6 символов"
            )

        if not any(c.isdigit() for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пароль должен содержать минимум одну цифру"
            )

        if not any(c.isalpha() for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пароль должен содержать минимум одну букву"
            )

    def validate_username_format(self, username: str) -> None:
        """Валидация формата имени пользователя.

        Args:
            username: Имя пользователя для проверки

        Raises:
            HTTPException: 400 если формат имени пользователя неверный
        """
        if len(username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Имя пользователя должно содержать минимум 3 символа"
            )

        if len(username) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Имя пользователя должно содержать максимум 50 символов"
            )

        if not username.replace("_", "").replace("-", "").isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя пользователя может содержать только буквы, цифры, дефисы и подчеркивания",
            )

    def validate_role_exists(self, role: str) -> AdminRole:
        """Валидация существования роли.

        Args:
            role: Роль для проверки

        Returns:
            AdminRole: Валидная роль

        Raises:
            HTTPException: 400 если роль не существует
        """
        try:
            return AdminRole(role)
        except ValueError:
            valid_roles = [role.value for role in AdminRole]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неверная роль. Доступные роли: {', '.join(valid_roles)}",
            )

    def validate_token_payload(self, payload: dict) -> str:
        """Валидация payload JWT токена.

        Args:
            payload: Декодированный payload JWT токена

        Returns:
            str: ID пользователя из токена

        Raises:
            AuthenticationError: Если токен недействителен
        """
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Недействительный токен")
        return str(user_id)

    def validate_email_format(self, email: str) -> None:
        """Валидация формата email от клиента.

        Args:
            email: Email для проверки

        Raises:
            HTTPException: 400 если формат email неверный
        """
        try:
            validate_email(email, check_deliverability=settings.email_dns_check)
        except EmailNotValidError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный формат email адреса")

    def validate_email_unique(self, existing_admin: Optional[AdminUser], exclude_id: Optional[int] = None) -> None:
        """Валидация уникальности email.

        Args:
            existing_admin: Существующий администратор (уже полученный из БД)
            exclude_id: ID администратора для исключения из проверки (при обновлении)

        Raises:
            HTTPException: 400 если email уже существует
        """
        if existing_admin and (exclude_id is None or existing_admin.id != exclude_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Администратор с таким email уже существует"
            )

    def validate_login_format(self, login: str) -> None:
        """Валидация формата логина (email или username).

        Args:
            login: Логин для проверки

        Raises:
            HTTPException: 400 если формат логина неверный
        """
        # Если содержит @ - проверяем как email
        if "@" in login:
            self.validate_email_format(login)
        else:
            # Проверяем как username
            self.validate_login_username_format(login)

    def validate_login_username_format(self, username: str) -> None:
        """Валидация формата username при входе в систему (более мягкая проверка).

        Args:
            username: Username для проверки

        Raises:
            HTTPException: 400 если формат username неверный
        """
        if len(username) < 3 or len(username) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username должен содержать от 3 до 255 символов"
            )

        if not username.replace("_", "").replace("-", "").replace(".", "").isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username может содержать только буквы, цифры, дефисы, точки и подчеркивания",
            )

    def validate_admin_authenticated(self, admin: Optional[AdminUser]) -> AdminUser:
        """Валидация успешной аутентификации администратора.

        Args:
            admin: Результат аутентификации (может быть None)

        Returns:
            AdminUser: Подтвержденного аутентифицированного администратора

        Raises:
            HTTPException: 401 если аутентификация не удалась
        """
        if not isinstance(admin, AdminUser):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные или несуществующий аккаунт",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return admin


admin_user_validator = AdminUserValidator()
