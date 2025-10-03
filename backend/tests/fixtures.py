"""Фикстуры данных для тестов."""

import datetime

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.admin_user import AdminUser
from backend.models.enums import AccessLevel
from backend.models.menu_item import MenuItem
from backend.models.message_template import MessageTemplate
from backend.models.telegram_user import TelegramUser


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession):
    """Создать администратора.

    Пароль: 'testpassword123'
    """
    # Это хеш пароля 'testpassword123' (bcrypt)
    # Сгенерирован заранее для тестов
    user = AdminUser(
        username="testadmin",
        password_hash="$2a$12$NCEkTSWzEITAb/MSfgUYMenYlUi/i0GDTGnm6X7aX3J7WdTdMA3Qq",
        is_active=True,
        email="admin@mail.com"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def user_free(db: AsyncSession):
    """Создать бесплатного пользователя."""
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
    """Создать премиум пользователя."""
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
    """Создать тестовые элементы меню."""
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


@pytest_asyncio.fixture
async def active_template(freezer, db: AsyncSession):
    freezer.move_to("2024-10-10")
    template = MessageTemplate(
        name="Active template",
        message_template="Message for active template",
        is_active=True,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@pytest_asyncio.fixture
async def inactive_template(freezer, db: AsyncSession):
    freezer.move_to("2024-10-10")
    template = MessageTemplate(
        name="Inactive template",
        message_template="Message for inactive template",
        is_active=False,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template