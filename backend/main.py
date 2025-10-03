"""Точка входа в приложение FastAPI."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from backend.api.routers import api_router
from backend.core.config import settings
from backend.core.db import AsyncSessionLocal
from backend.core.exception_handlers import register_exception_handlers
from backend.core.security import get_password_hash
from backend.models import AdminUser
from backend.models.enums import AdminRole


# Желательно потом почистить файл и раскидать по файлам, где нужно
# логировани, middleware, настройки, endpoints и т.д.

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# TODO: Перенести настройки логирования в отдельный файл
# Сюда импортировать готовый logger
# Настроить логирование в файл


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    logger.info("Запуск приложения FastAPI")
    await ensure_default_admin()
    yield
    # Shutdown
    logger.info("Завершение работы приложения FastAPI")


def create_app() -> FastAPI:
    """Создание и настройка FastAPI приложения."""
    app = FastAPI(
        title="I Hear You Bot API",
        description="API для управления Telegram-ботом 'Я тебя слышу'",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Регистрация глобальных обработчиков исключений
    register_exception_handlers(app)

    # Подключение роутеров API
    app.include_router(api_router)

    return app


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


# Создание экземпляра приложения
app = create_app()


@app.get("/")
async def root():
    """Корневой эндпойнт."""
    return {"message": "I Hear You Bot API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def api_health_check():
    """Проверка работоспособности API."""
    try:
        # Проверяем подключение к базе данных
        async with AsyncSessionLocal() as session:
            await session.execute(select(1))

        return {"status": "healthy", "service": "api", "version": "1.0.0", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "api",
            "version": "1.0.0",
            "database": "disconnected",
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower(),
    )
