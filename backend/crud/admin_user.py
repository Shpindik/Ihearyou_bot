"""CRUD операции для администраторов."""

from __future__ import annotations

from typing import Optional

from pydantic import EmailStr
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import get_password_hash, verify_password
from backend.models.admin_user import AdminUser
from backend.models.enums import AdminRole

from .base import BaseCRUD


class AdminUserCRUD(BaseCRUD[AdminUser, dict, dict]):
    """CRUD операции для модели AdminUser."""

    def __init__(self):
        """Инициализация CRUD для администраторов."""
        super().__init__(AdminUser)

    async def get_by_id(self, db: AsyncSession, admin_id: int) -> Optional[AdminUser]:
        """Получить администратора по ID."""
        return await self.get(db, admin_id)

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[AdminUser]:
        """Получить администратора по имени пользователя."""
        result = await db.execute(select(AdminUser).where(AdminUser.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: EmailStr) -> Optional[AdminUser]:
        """Получить администратора по email."""
        result = await db.execute(select(AdminUser).where(AdminUser.email == email))
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, db: AsyncSession, login: str) -> Optional[AdminUser]:
        """Получить администратора по email или username."""
        result = await db.execute(select(AdminUser).where(or_(AdminUser.email == login, AdminUser.username == login)))
        return result.scalar_one_or_none()

    async def authenticate(self, db: AsyncSession, username: str, password: str) -> Optional[AdminUser]:
        """Аутентификация администратора по имени пользователя и паролю."""
        admin = await self.get_by_username(db, username)
        if not admin:
            return None
        if not verify_password(password, admin.password_hash):
            return None
        return admin

    async def create_admin(
        self,
        db: AsyncSession,
        username: str,
        email: EmailStr,
        password: str,
        role: AdminRole = AdminRole.ADMIN,
        is_active: bool = True,
    ) -> AdminUser:
        """Создать нового администратора с email."""
        password_hash = get_password_hash(password)
        admin = AdminUser(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin

    async def update_password(self, db: AsyncSession, admin: AdminUser, new_password: str) -> AdminUser:
        """Обновить пароль администратора."""
        admin.password_hash = get_password_hash(new_password)
        await db.commit()
        await db.refresh(admin)
        return admin

    async def update_role(self, db: AsyncSession, admin: AdminUser, new_role: AdminRole) -> AdminUser:
        """Обновить роль администратора."""
        admin.role = new_role
        await db.commit()
        await db.refresh(admin)
        return admin

    async def deactivate(self, db: AsyncSession, admin: AdminUser) -> AdminUser:
        """Деактивировать администратора."""
        admin.is_active = False
        await db.commit()
        await db.refresh(admin)
        return admin

    async def activate(self, db: AsyncSession, admin: AdminUser) -> AdminUser:
        """Активировать администратора."""
        admin.is_active = True
        await db.commit()
        await db.refresh(admin)
        return admin

    async def update_email(self, db: AsyncSession, admin: AdminUser, new_email: EmailStr) -> AdminUser:
        """Обновить email администратора."""
        admin.email = new_email
        await db.commit()
        await db.refresh(admin)
        return admin


admin_user_crud = AdminUserCRUD()
