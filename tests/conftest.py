"""Конфигурация pytest для тестов поиска.

Этот файл содержит общие фикстуры для всех тестов.
"""

import asyncio
import datetime
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from backend.core.db import Base, get_session
from backend.main import app
from backend.models.enums import AccessLevel
from backend.models.menu_item import MenuItem
from backend.models.telegram_user import TelegramUser


TEST_DATABASE_URL = "sqlite+aiosqlite:///file::memory:?cache=shared"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Event loop фикстура
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создать event loop для всей сессии тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# База данных фикстуры

@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Создать сессию БД для каждого теста."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocal() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Создать async HTTP клиент для тестирования API."""

    async def override_get_session():
        yield db

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_free(db: AsyncSession):
    user = TelegramUser(
        telegram_id=123456789,
        username="freeuser",
        first_name="Free",
        last_name=None,
        subscription_type=AccessLevel.FREE,
        created_at=datetime.datetime.now(datetime.UTC),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user.telegram_id


@pytest_asyncio.fixture
async def user_premium(db: AsyncSession):
    user = TelegramUser(
        telegram_id=987654321,
        username="premiumuser",
        first_name="Premium",
        last_name=None,
        subscription_type=AccessLevel.PREMIUM,
        created_at=datetime.datetime.now(datetime.UTC),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user.telegram_id


@pytest_asyncio.fixture
async def menu_items_fixture(db: AsyncSession):
    items = [
        MenuItem(
            title="Test Free Item",
            description="Test description",
            is_active=True,
            access_level=AccessLevel.FREE,
        ),
        MenuItem(
            title="Test Premium Item",
            description="Premium description",
            is_active=True,
            access_level=AccessLevel.PREMIUM,
        ),
        MenuItem(
            title="Inactive Item",
            description="inactive",
            is_active=False,
            access_level=AccessLevel.PREMIUM,
        ),
        MenuItem(
            title="Русский тест",
            description="Описание на русском",
            is_active=True,
            access_level=AccessLevel.PREMIUM,
        ),
    ]
    db.add_all(items)
    await db.commit()
    for item in items:
        await db.refresh(item)
        db.expunge(item)
    return items


@pytest.fixture
def anyio_backend():
    """Указать backend для anyio (используется pytest-asyncio)."""
    return "asyncio"
