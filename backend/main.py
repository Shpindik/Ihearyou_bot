"""Точка входа в приложение FastAPI."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from core.config import settings
from core.db import AsyncSessionLocal
from core.security import get_password_hash
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import AdminUser
from sqlalchemy import select

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
    # await ensure_default_admin()  # Временно отключено
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

    # Подключение роутеров API
    from api.routers import api_router

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
                    email=settings.admin_email,
                    password_hash=password_hash,
                    role="admin",
                    is_active=True,
                )
                session.add(admin_user)
                logger.info(f"Создан администратор по умолчанию: {settings.admin_username}")
            else:
                # Обновляем пароль и активируем
                admin_user.password_hash = password_hash
                admin_user.is_active = True
                admin_user.role = admin_user.role or "admin"
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
async def health_check():
    """Проверка здоровья приложения."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level=settings.log_level.lower())
