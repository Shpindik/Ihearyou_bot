"""CRUD операции для администраторов."""

from __future__ import annotations

from typing import List, Optional

from pydantic import EmailStr
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import verify_password
from backend.models.admin_user import AdminUser
from backend.models.enums import AdminRole

from .base import BaseCRUD


class AdminUserCRUD(BaseCRUD[AdminUser, dict, dict]):
    """CRUD операции для модели AdminUser."""

    def __init__(self):
        """Инициализация CRUD для администраторов."""
        super().__init__(AdminUser)

    async def get_by_id(self, db: AsyncSession, *, admin_id: int) -> Optional[AdminUser]:
        """Получить администратора по ID."""
        return await self.get(db, id=admin_id)

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
        *,
        username: str,
        email: EmailStr,
        password_hash: str,
        role: AdminRole = AdminRole.ADMIN,
        is_active: bool = True,
    ) -> AdminUser:
        """Создать нового администратора."""
        admin_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "is_active": is_active,
        }

        admin = AdminUser(**admin_data)
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin

    async def update_password(self, db: AsyncSession, *, admin: AdminUser, password_hash: str) -> AdminUser:
        """Обновить хеш пароля администратора.

        Args:
            db: Сессия базы данных
            admin: Администратор для обновления
            password_hash: Готовый хеш пароля (хэширование должно быть в сервисе)
        """
        admin.password_hash = password_hash
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin

    async def update_role(self, db: AsyncSession, *, admin: AdminUser, role: AdminRole) -> AdminUser:
        """Обновить роль администратора."""
        admin.role = role
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin

    async def deactivate(self, db: AsyncSession, *, admin: AdminUser) -> AdminUser:
        """Деактивировать администратора."""
        admin.is_active = False
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin

    async def activate(self, db: AsyncSession, *, admin: AdminUser) -> AdminUser:
        """Активировать администратора."""
        admin.is_active = True
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin

    async def update_email(self, db: AsyncSession, *, admin: AdminUser, email: EmailStr) -> AdminUser:
        """Обновить email администратора."""
        admin.email = email
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin

    async def update_admin_info(
        self,
        db: AsyncSession,
        *,
        admin: AdminUser,
        username: Optional[str] = None,
        email: Optional[EmailStr] = None,
        role: Optional[AdminRole] = None,
        is_active: Optional[bool] = None,
    ) -> AdminUser:
        """Обновить информацию об администраторе."""
        if username is not None:
            admin.username = username
        if email is not None:
            admin.email = email
        if role is not None:
            admin.role = role
        if is_active is not None:
            admin.is_active = is_active

        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin

    async def get_all_admins(self, db: AsyncSession) -> List[AdminUser]:
        """Получить всех администраторов."""
        result = await db.execute(select(AdminUser).order_by(AdminUser.created_at.desc()))
        return result.scalars().all()


admin_user_crud = AdminUserCRUD()
