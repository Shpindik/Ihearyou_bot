"""Конфигурация pytest для тестов."""

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from backend.core.db import Base, get_session
from backend.core.dependencies import require_admin_role
from backend.core.security import create_access_token
from backend.models.enums import AdminRole
from backend.main import app
from backend.tests.fixtures import (
    active_template,
    admin_user,
    inactive_template,
    menu_items_fixture,
    user_free,
    user_premium,
)


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

TEST_DB = BASE_DIR / "test.db"
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{str(TEST_DB)}"

test_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создать event loop для всей сессии тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Создать сессию БД для каждого теста."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocal() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def valid_admin_token(admin_user):
    """Generate a valid JWT token"""
    payload = {
        "sub": str(admin_user.id),
        "username": admin_user.username,
        "role": admin_user.role,
    }
    return create_access_token(data=payload, expires_delta=timedelta(minutes=60))


@pytest.fixture
def admin_headers(valid_admin_token):
    """Generate authorization headers with admin token"""
    return {"Authorization": f"Bearer {valid_admin_token}"}


@pytest_asyncio.fixture(scope="function")
async def admin_client(db: AsyncSession, admin_headers) -> AsyncGenerator[AsyncClient, None]:
    """Создать async HTTP клиент для тестирования API."""

    async def override_get_session():
        yield db

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers.update(admin_headers)
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Создать async HTTP клиент для тестирования API."""

    async def override_get_session():
        yield db

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def anyio_backend():
    """Указать backend для anyio (используется pytest-asyncio)."""
    return "asyncio"
