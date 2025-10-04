"""Конфигурация pytest для тестов."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from backend.core.db import Base, get_session
from backend.core.dependencies import (
    Admin,
    get_current_active_admin,
    require_admin_role,
    require_moderator_or_admin_role,
)
from backend.core.security import create_access_token
from backend.main import app

from backend.tests.fixtures import (
    active_template,
    admin_user,
    admin_user_crud,
    admin_user_service,
    admin_user_validator,
    analytics_crud,
    analytics_service,
    analytics_validator,
    email_service,
    inactive_template,
    menu_item_crud,
    menu_items_fixture,
    moderator_user,
    telegram_users_fixture,
    telegram_user_crud,
    user_free,
    user_premium,
)


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


@pytest.fixture(scope="function")
def database_url(postgresql):
    """Создает URL для тестовой PostgreSQL базы данных из fixture postgresql."""
    info = postgresql.info
    return f"postgresql+asyncpg://{info.user}:{info.password}@{info.host}:{info.port}/{info.dbname}"


@pytest_asyncio.fixture(scope="function")
async def postgresql_async_engine(database_url):
    """Создает асинхронный SQLAlchemy engine для PostgreSQL."""
    engine = create_async_engine(
        database_url,
        echo=False,
        poolclass=NullPool,
    )

    # Создаем все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Закрываем engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(postgresql_async_engine) -> AsyncSession:
    """Создает сессию базы данных для каждого теста."""
    # Создаем сессию
    async_session = sessionmaker(
        postgresql_async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    session = async_session()

    # Очищаем таблицы перед каждым тестом
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())
    await session.commit()

    try:
        yield session
    finally:
        # Откатываем изменения после теста
        await session.rollback()
        await session.close()


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создать event loop для всей сессии тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db(db_session: AsyncSession) -> AsyncSession:
    """Псевдоним для db_session для совместимости с fixtures."""
    return db_session


@pytest_asyncio.fixture(scope="function")
async def async_client(db: AsyncSession, admin_user) -> AsyncGenerator[AsyncClient, None]:
    """Создать async HTTP клиент для тестирования API с mock аутентификацией."""

    async def override_get_session():
        yield db

    app.dependency_overrides[get_session] = override_get_session

    # Mock dependencies для аутентификации в тестах
    def mock_get_current_active_admin():
        return admin_user

    def mock_require_admin_role():
        return admin_user

    def mock_require_moderator_or_admin_role():
        return admin_user

    def mock_admin():
        return admin_user

    app.dependency_overrides[get_current_active_admin] = mock_get_current_active_admin
    app.dependency_overrides[require_admin_role] = mock_require_admin_role
    app.dependency_overrides[require_moderator_or_admin_role] = mock_require_moderator_or_admin_role
    app.dependency_overrides[Admin] = mock_admin

    # Прямой вызов ASGI приложения
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver", follow_redirects=True) as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client_no_auth(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Создать async HTTP клиент для тестирования API без mock аутентификации."""

    async def override_get_session():
        yield db

    app.dependency_overrides[get_session] = override_get_session

    # Прямой вызов ASGI приложения без mock аутентификации
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver", follow_redirects=True) as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client_moderator(db: AsyncSession, moderator_user) -> AsyncGenerator[AsyncClient, None]:
    """Создать async HTTP клиент для тестирования API с аутентификацией модератора."""

    async def override_get_session():
        yield db

    app.dependency_overrides[get_session] = override_get_session

    # Mock dependencies для аутентификации модератора (без mock ролей)
    def mock_get_current_active_admin():
        return moderator_user

    def mock_admin():
        return moderator_user

    app.dependency_overrides[get_current_active_admin] = mock_get_current_active_admin
    app.dependency_overrides[Admin] = mock_admin

    # Прямой вызов ASGI приложения
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver", follow_redirects=True) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def anyio_backend():
    """Указать backend для anyio (используется pytest-asyncio)."""
    return "asyncio"


@pytest_asyncio.fixture
async def admin_token(admin_user) -> str:
    """Получить JWT токен администратора для тестирования."""
    token_data = {"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role}
    return create_access_token(token_data)


@pytest_asyncio.fixture
async def moderator_token(moderator_user) -> str:
    """Получить JWT токен модератора для тестирования."""
    token_data = {"sub": str(moderator_user.id), "username": moderator_user.username, "role": moderator_user.role}
    return create_access_token(token_data)


# Алиасы для обратной совместимости
admin_client = async_client
