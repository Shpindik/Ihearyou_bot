"""Сервис для работы с административными пользователями."""

from __future__ import annotations

from datetime import timedelta
from typing import Optional

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.exceptions import AuthenticationError, NotFoundError
from backend.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    verify_password_reset_token,
    verify_token,
)
from backend.crud.admin_user import admin_user_crud
from backend.models.admin_user import AdminUser
from backend.models.enums import AdminRole
from backend.schemas.admin.auth import (
    AdminLoginResponse,
    AdminMeResponse,
    AdminPasswordResetSuccessResponse,
    AdminRefreshResponse,
)
from backend.utils.email import email_service
from backend.validators.admin_user import admin_user_validator


class AdminUserService:
    """Сервис для работы с административными пользователями."""

    def __init__(self):
        """Инициализация сервиса Admin User."""
        self.admin_crud = admin_user_crud
        self.validator = admin_user_validator

    async def authenticate_admin_by_token(self, session: AsyncSession, token: str) -> AdminUser:
        """Аутентификация администратора по JWT токену.

        Args:
            session: Сессия базы данных
            token: JWT токен

        Returns:
            AdminUser: Аутентифицированный администратор
        """
        # Декодируем токен
        payload = verify_token(token)
        user_id = self.validator.validate_token_payload(payload)

        # Получаем пользователя из базы данных
        admin_user = await self.admin_crud.get_by_id(session, int(user_id))

        # Валидируем полученные данные
        admin_user = self.validator.validate_admin_exists(admin_user)
        admin_user = self.validator.validate_admin_active(admin_user)

        return admin_user

    async def authenticate_admin_by_credentials(
        self, session: AsyncSession, username: str, password: str
    ) -> Optional[AdminUser]:
        """Аутентификация администратора по имени пользователя и паролю.

        Args:
            session: Сессия базы данных
            username: Имя пользователя
            password: Пароль

        Returns:
            Optional[AdminUser]: Аутентифицированный администратор или None
        """
        return await self.admin_crud.authenticate(session, username, password)

    async def authenticate_admin_by_login_and_password(
        self, session: AsyncSession, login: str, password: str
    ) -> Optional[AdminUser]:
        """Аутентификация администратора по email ИЛИ username + паролю.

        Args:
            session: Сессия базы данных
            login: Email или username
            password: Пароль

        Returns:
            Optional[AdminUser]: Аутентифицированный администратор или None
        """
        self.validator.validate_login_format(login)

        admin = await self.admin_crud.get_by_email_or_username(session, login)
        if not admin:
            return None
        from backend.core.security import verify_password

        if not verify_password(password, admin.password_hash):
            return None
        return admin

    async def get_admin_by_id(self, session: AsyncSession, admin_id: int) -> Optional[AdminUser]:
        """Получить администратора по ID.

        Args:
            session: Сессия базы данных
            admin_id: ID администратора

        Returns:
            Optional[AdminUser]: Администратор или None
        """
        return await self.admin_crud.get_by_id(session, admin_id)

    async def get_admin_by_username(self, session: AsyncSession, username: str) -> Optional[AdminUser]:
        """Получить администратора по имени пользователя.

        Args:
            session: Сессия базы данных
            username: Имя пользователя

        Returns:
            Optional[AdminUser]: Администратор или None
        """
        return await self.admin_crud.get_by_username(session, username)

    async def login_admin(self, session: AsyncSession, username: str, password: str) -> "AdminLoginResponse":
        """Аутентификация администратора и создание токенов.

        Args:
            session: Сессия базы данных
            username: Имя пользователя
            password: Пароль

        Returns:
            AdminLoginResponse: Ответ с токенами аутентификации

        Raises:
            AuthenticationError: Если учетные данные неверны
        """
        # Аутентификация пользователя
        admin = await self.authenticate_admin_by_credentials(session, username, password)

        if not admin:
            raise AuthenticationError("Неверное имя пользователя или пароль")

        # Создание токенов
        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(admin.id), "username": admin.username, "role": admin.role},
            expires_delta=access_token_expires,
        )

        refresh_token = create_refresh_token(data={"sub": str(admin.id), "type": "refresh"})

        return AdminLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
        )

    async def refresh_access_token(self, session: AsyncSession, refresh_token: str) -> "AdminRefreshResponse":
        """Обновление токена доступа с помощью refresh токена.

        Args:
            session: Сессия базы данных
            refresh_token: Refresh токен

        Returns:
            AdminRefreshResponse: Ответ с новым access токеном

        Raises:
            AuthenticationError: Если refresh токен недействителен
            NotFoundError: Если пользователь не найден
        """
        # Декодируем refresh токен
        payload = verify_token(refresh_token)
        user_id = self.validator.validate_token_payload(payload)
        token_type = payload.get("type")

        if token_type != "refresh":
            raise AuthenticationError("Недействительный refresh токен")

        # Получаем пользователя
        admin = await self.get_admin_by_id(session, int(user_id))

        if not admin:
            raise NotFoundError("Пользователь не найден")

        # Создаем новый access токен
        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(admin.id), "username": admin.username, "role": admin.role},
            expires_delta=access_token_expires,
        )

        return AdminRefreshResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
        )

    def get_current_admin_info(self, admin: AdminUser) -> AdminMeResponse:
        """Получение информации о текущем администраторе.

        Args:
            admin: Объект администратора

        Returns:
            AdminMeResponse: Информация об администраторе
        """
        return AdminMeResponse(
            id=admin.id,
            username=admin.username,
            email=admin.email,
            role=admin.role.value,
            is_active=admin.is_active,
            created_at=admin.created_at.isoformat(),
        )

    async def create_admin(
        self,
        session: AsyncSession,
        username: str,
        email: EmailStr,
        password: str,
        role: AdminRole = AdminRole.ADMIN,
        is_active: bool = True,
    ) -> AdminUser:
        """Создать нового администратора с email.

        Args:
            session: Сессия базы данных
            username: Имя пользователя
            email: Email администратора
            password: Пароль
            role: Роль администратора
            is_active: Активность пользователя

        Returns:
            AdminUser: Созданный администратор
        """
        # Валидация входных данных
        self.validator.validate_username_format(username)
        self.validator.validate_email_format(email)
        self.validator.validate_password_strength(password)

        # Проверяем уникальность username и email
        existing_user = await self.admin_crud.get_by_email_or_username(session, username)
        self.validator.validate_username_unique(existing_user)

        existing_email = await self.admin_crud.get_by_email(session, email)
        self.validator.validate_email_unique(existing_email)

        return await self.admin_crud.create_admin(session, username, email, password, role, is_active)

    async def update_admin_password(self, session: AsyncSession, admin: AdminUser, new_password: str) -> AdminUser:
        """Обновить пароль администратора.

        Args:
            session: Сессия базы данных
            admin: Администратор
            new_password: Новый пароль

        Returns:
            AdminUser: Обновленный администратор
        """
        # Валидация пароля
        self.validator.validate_password_strength(new_password)

        return await self.admin_crud.update_password(session, admin, new_password)

    async def update_admin_role(self, session: AsyncSession, admin: AdminUser, new_role: AdminRole) -> AdminUser:
        """Обновить роль администратора.

        Args:
            session: Сессия базы данных
            admin: Администратор
            new_role: Новая роль

        Returns:
            AdminUser: Обновленный администратор
        """
        return await self.admin_crud.update_role(session, admin, new_role)

    async def deactivate_admin(self, session: AsyncSession, admin: AdminUser) -> AdminUser:
        """Деактивировать администратора.

        Args:
            session: Сессия базы данных
            admin: Администратор

        Returns:
            AdminUser: Деактивированный администратор
        """
        return await self.admin_crud.deactivate(session, admin)

    async def activate_admin(self, session: AsyncSession, admin: AdminUser) -> AdminUser:
        """Активировать администратора.

        Args:
            session: Сессия базы данных
            admin: Администратор

        Returns:
            AdminUser: Активированный администратор
        """
        return await self.admin_crud.activate(session, admin)

    async def get_admin_by_email(self, session: AsyncSession, email: EmailStr) -> Optional[AdminUser]:
        """Получить администратора по email.

        Args:
            session: Сессия базы данных
            email: Email администратора

        Returns:
            Optional[AdminUser]: Администратор или None
        """
        return await self.admin_crud.get_by_email(session, email)

    async def initialize_password_reset(self, session: AsyncSession, email: EmailStr) -> dict:
        """Инициировать восстановление пароля.

        Args:
            session: Сессия базы данных
            email: Email для восстановления пароля

        Returns:
            dict: Ответ с информацией о статусе
        """
        admin = await self.get_admin_by_email(session, email)

        # Поведение должно быть одинаковым независимо от существования email
        # для безопасности (защита от перебора email адресов)
        if admin:
            admin_email = self.validator.validate_admin_exists(admin)
            admin_verified = self.validator.validate_admin_active(admin_email)

            # Создаем токен восстановления
            reset_token = create_password_reset_token(email=admin_verified.email)

            # Отправляем письмо
            await email_service.send_password_reset_email(
                email=admin_verified.email, reset_token=reset_token, admin_name=admin_verified.username
            )

        # Всегда возвращаем одинаковый ответ
        return {"message": "Если email существует в системе, письмо с инструкциями отправлено"}

    async def confirm_password_reset(
        self, session: AsyncSession, token: str, new_password: str
    ) -> AdminPasswordResetSuccessResponse:
        """Подтвердить восстановление пароля.

        Args:
            session: Сессия базы данных
            token: Токен восстановления
            new_password: Новый пароль

        Returns:
            AdminPasswordResetSuccessResponse: Ответ с новыми токенами
        """
        # Декодируем токен
        email = verify_password_reset_token(token)
        if not email:
            raise AuthenticationError("Недействительный или истекший токен восстановления")

        # Получаем администратора
        admin = await self.get_admin_by_email(session, email)
        admin_verified = self.validator.validate_admin_exists(admin)
        admin_active = self.validator.validate_admin_active(admin_verified)

        # Валидируем новый пароль
        self.validator.validate_password_strength(new_password)

        # Обновляем пароль
        updated_admin = await self.admin_crud.update_password(session, admin_active, new_password)

        # Создаем новые токены para автоматического входа
        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(updated_admin.id), "username": updated_admin.username, "role": updated_admin.role},
            expires_delta=access_token_expires,
        )

        refresh_token = create_refresh_token(data={"sub": str(updated_admin.id), "type": "refresh"})

        return AdminPasswordResetSuccessResponse(
            message="Пароль успешно изменен",
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
        )


admin_user_service = AdminUserService()
