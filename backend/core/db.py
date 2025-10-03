"""Подключение к БД."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from .config import settings


# Базовый класс для всех моделей
Base = declarative_base()

# Создание асинхронного движка
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=20,
    max_overflow=30,
)

# Фабрика асинхронных сессий с правильным управлением транзакциями
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

# Scoped session для thread-local безопасности в многопоточной среде
AsyncSessionLocal = async_scoped_session(async_session_factory, scopefunc=lambda: None)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии базы данных.

    AsyncSession обеспечивает автоматическое управление транзакциями:
    - Контекстный менеджер автоматически закрывает сессию
    - Для управления транзакциями используется async with session.begin()
    """
    async with AsyncSessionLocal() as session:
        yield session
