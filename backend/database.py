from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv(
    "ADMIN_DATABASE_URL",
    "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", 5432),
        db=os.getenv("POSTGRES_DB", "db"),
    ),
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
