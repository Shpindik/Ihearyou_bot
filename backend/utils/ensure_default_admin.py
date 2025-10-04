import logging

from sqlalchemy import select

from backend.core.config import settings
from backend.core.db import AsyncSessionLocal
from backend.core.security import get_password_hash
from backend.models.admin_user import AdminUser
from backend.models.enums import AdminRole


logger = logging.getLogger(__name__)


async def ensure_default_admin() -> None:
    """Создание администратора по умолчанию при запуске."""
    try:
        async with AsyncSessionLocal() as session:
            # Проверяем существование администратора
            result = await session.execute(select(AdminUser).where(AdminUser.username == settings.admin_username))
            admin_user = result.scalar_one_or_none()

            # Создаем или обновляем администратора
            password_hash = get_password_hash(settings.admin_password)

            if admin_user is None:
                admin_user = AdminUser(
                    username=settings.admin_username,
                    email=settings.admin_email or "admin@yourapp.com",
                    password_hash=password_hash,
                    role=AdminRole.ADMIN,
                    is_active=True,
                )
                session.add(admin_user)
                logger.info(f"Создан администратор по умолчанию: {settings.admin_username} ({settings.admin_email})")
            else:
                # Обновляем данные и активируем
                admin_user.password_hash = password_hash
                admin_user.is_active = True
                admin_user.role = admin_user.role or AdminRole.ADMIN
                admin_user.email = settings.admin_email or "admin@yourapp.com"
                logger.info(f"Обновлен администратор: {settings.admin_username}")

            await session.commit()

    except Exception as e:
        logger.error(f"Ошибка при создании администратора по умолчанию: {e}")
        raise
